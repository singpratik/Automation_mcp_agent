# Security Guidelines

## Environment Variables
- Never commit `.env` files to version control
- Use `.env.example` as a template
- Store sensitive credentials in environment variables or secure vaults

## API Security
- All API endpoints include input validation
- SSRF protection implemented for external requests
- Path traversal protection for file operations

## Browser Security
- Media file paths (audio/video) are validated before use
- Browser processes are properly cleaned up
- Media permissions are controlled

## Database Security
- SQL connections use context managers to prevent resource leaks
- Input parsing handles quoted values safely

## XSS Prevention
- All user input is HTML-escaped before rendering
- Streamlit unsafe_allow_html is used carefully

## Credentials Management
- OpenAI API keys loaded from environment
- VMock credentials configurable via environment variables
- No hardcoded secrets in source code

## File Operations
- Path validation prevents directory traversal
- Operations restricted to safe directories
- Proper error handling for file system operations