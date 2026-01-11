# ReviewMate - AI-Powered Code Review Assistant

An intelligent code review tool that uses AI agents to analyze code diffs for quality, security, and performance issues.

## Features

- **Multi-Agent Analysis**: Specialized agents for code quality, security scanning, and performance optimization
- **RAG Integration**: Retrieval-augmented generation using coding best practices
- **Web Dashboard**: React frontend for easy diff analysis
- **GitHub Integration**: Automated PR reviews via Actions
- **Local Operation**: Runs entirely on localhost with free AI APIs

## Quick Start

### Prerequisites
- Python 3.11+, Node.js 18+

### Backend
```bash
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
npm install
npm start  # Opens http://localhost:3000
```

### Environment
Create `.env` with:
```
GROQ_API_KEY=your_groq_api_key_here
```

## Usage

1. Start backend and frontend
2. Paste Git diff in web UI
3. Get AI analysis

## Testing
```bash
python -m pytest tests/ -v
```
