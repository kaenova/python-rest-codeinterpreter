# python-rest-codeinterpreter

A REST API for Python Code Interpreter with session-based execution.

## Features

- **Session-based execution**: Execute Python code in isolated sessions
- **Session persistence**: Continue execution in the same session by providing session_id
- **Automatic cleanup**: Sessions are automatically destroyed after 5 minutes of inactivity
- **Common libraries pre-installed**: numpy, pandas, matplotlib, scipy, and more
- **Fast session creation**: Optimized for quick session initialization
- **Docker support**: Easy deployment with Docker

## Quick Start

### Using Docker

Build and run the Docker container:

```bash
docker build -t python-code-interpreter .
docker run -p 8000:8000 python-code-interpreter
```

Or use docker-compose:

```bash
docker-compose up --build
```

### Local Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
# or
uvicorn app:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

### Endpoints

#### `GET /`
Health check endpoint. Returns API status and number of active sessions.

#### `POST /run`
Execute Python code in a session.

**Request Body:**
```json
{
  "code": "print('Hello, World!')",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "stdout": "Hello, World!\n",
  "stderr": "",
  "session_id": "generated-or-provided-session-id"
}
```

## Usage Examples

### Example 1: Simple execution (new session)

```bash
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")"
  }'
```

Response:
```json
{
  "stdout": "Hello, World!\n",
  "stderr": "",
  "session_id": "abc-123-def-456"
}
```

### Example 2: Continue in same session

```bash
# First request - set a variable
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "x = 42"
  }'

# Second request - use the variable (with session_id from first response)
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(x * 2)",
    "session_id": "abc-123-def-456"
  }'
```

### Example 3: Using numpy

```bash
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import numpy as np\nprint(np.array([1, 2, 3]).mean())"
  }'
```

### Example 4: Error handling

```bash
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(undefined_variable)"
  }'
```

Response:
```json
{
  "stdout": "",
  "stderr": "NameError: name 'undefined_variable' is not defined\n",
  "session_id": "abc-123-def-456"
}
```

## Pre-installed Libraries

The following libraries are pre-installed and ready to use:

- **numpy**: Numerical computing
- **pandas**: Data manipulation and analysis
- **matplotlib**: Plotting and visualization
- **scipy**: Scientific computing
- **requests**: HTTP library

## Session Management

- Sessions are automatically created if no `session_id` is provided
- Sessions remain active for 5 minutes after last use
- Inactive sessions are automatically cleaned up to free resources
- Each session has its own isolated namespace

## Architecture

- **FastAPI**: Modern web framework for building APIs
- **Session Manager**: Handles session lifecycle and cleanup
- **Isolated Namespaces**: Each session maintains its own variable scope
- **Thread-safe**: Uses locks to ensure concurrent session access is safe

## Security Considerations

⚠️ **Warning**: This service executes arbitrary Python code. Deploy with caution:

- Run in isolated environments (containers)
- Implement authentication/authorization
- Use network restrictions
- Monitor resource usage
- Consider using additional sandboxing (e.g., seccomp, AppArmor)

## Development

### Project Structure

```
.
├── app.py              # Main application code
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker Compose configuration
└── README.md          # This file
```

### Running Tests

```bash
# Manual testing
python app.py
```

## License

MIT
