# Automation MCP Agent

A multi-agent AI system with browser automation capabilities using browser-use library and Streamlit interface.

## Features

- 🤖 **Browser Agent**: AI-powered web automation with visual element detection
- 💬 **Multi-threaded Chat**: Conversation history with thread support
- 📊 **Real-time Logs**: Live action logs and debugging information
- 🐳 **Docker Support**: Containerized deployment
- 🎯 **Native browser-use Integration**: Full AI capabilities with visual highlighting

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install --with-deps
```

2. Set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

3. Run the application:
```bash
streamlit run streamlit_app.py
```

### Docker Deployment

1. Build the image:
```bash
docker build -t browser-agent .
```

2. Run the container:
```bash
docker run -p 8501:8501 -e OPENAI_API_KEY="your-key" browser-agent
```

3. Access at: http://localhost:8501

## Usage

1. Enter your task in the text area
2. Click "🚀 Run Browser Agent"
3. View real-time logs in the expandable sections
4. Monitor browser actions and AI reasoning

## Requirements

- Python 3.11+
- OpenAI API Key
- Docker (for containerized deployment)

## Architecture

- **Browser Agent**: Uses browser-use library for AI-powered web automation
- **Streamlit Interface**: Web-based UI with real-time logging
- **Multi-threading**: Supports concurrent chat sessions
- **Docker**: Containerized for easy deployment
