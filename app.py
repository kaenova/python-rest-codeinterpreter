import uuid
import sys
import io
import time
from contextlib import redirect_stdout, redirect_stderr
from typing import Optional, Dict, Any
from threading import Lock, Thread
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class CodeRequest(BaseModel):
    code: str
    session_id: Optional[str] = None


class CodeResponse(BaseModel):
    stdout: str
    stderr: str
    session_id: str


class Session:
    """Represents a Python execution session with its own namespace."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.namespace: Dict[str, Any] = {}
        self.last_used = datetime.now()
        
    def execute(self, code: str) -> tuple[str, str]:
        """Execute code in this session's namespace."""
        self.last_used = datetime.now()
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, self.namespace)
        except Exception as e:
            stderr_capture.write(f"{type(e).__name__}: {str(e)}\n")
        
        return stdout_capture.getvalue(), stderr_capture.getvalue()


class SessionManager:
    """Manages multiple Python execution sessions."""
    
    def __init__(self, timeout_minutes: int = 5):
        self.sessions: Dict[str, Session] = {}
        self.lock = Lock()
        self.timeout_minutes = timeout_minutes
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start a background thread to clean up expired sessions."""
        def cleanup_loop():
            while True:
                time.sleep(60)  # Check every minute
                self._cleanup_expired_sessions()
        
        thread = Thread(target=cleanup_loop, daemon=True)
        thread.start()
    
    def _cleanup_expired_sessions(self):
        """Remove sessions that haven't been used in timeout_minutes."""
        with self.lock:
            now = datetime.now()
            expired = [
                sid for sid, session in self.sessions.items()
                if now - session.last_used > timedelta(minutes=self.timeout_minutes)
            ]
            for sid in expired:
                del self.sessions[sid]
                print(f"Cleaned up expired session: {sid}")
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> Session:
        """Get an existing session or create a new one."""
        with self.lock:
            if session_id and session_id in self.sessions:
                return self.sessions[session_id]
            
            # Create new session
            new_id = session_id or str(uuid.uuid4())
            session = Session(new_id)
            self.sessions[new_id] = session
            return session


# Initialize FastAPI app and session manager
app = FastAPI(
    title="Python Code Interpreter REST API",
    description="Execute Python code in isolated sessions via REST API",
    version="1.0.0"
)
session_manager = SessionManager(timeout_minutes=5)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Python Code Interpreter REST API",
        "active_sessions": len(session_manager.sessions)
    }


@app.post("/run", response_model=CodeResponse)
async def run_code(request: CodeRequest):
    """
    Execute Python code in a session.
    
    - **code**: Python code to execute
    - **session_id**: Optional session ID to continue existing session
    
    Returns stdout, stderr, and session_id.
    """
    try:
        session = session_manager.get_or_create_session(request.session_id)
        stdout, stderr = session.execute(request.code)
        
        return CodeResponse(
            stdout=stdout,
            stderr=stderr,
            session_id=session.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
