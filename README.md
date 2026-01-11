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

## Automated PR Analysis Setup

Automatically analyze PRs with AI whenever they're opened or updated. One-time setup per repository.

### Prerequisites

- ReviewMate backend deployed or running locally (with tunneling)
- GitHub repository access

### Step-by-Step Setup

1. **Copy Workflow File**
   - Copy `.github/workflows/pull_request_review.yml` from ReviewMate repo to your target repo's `.github/workflows/` directory.
   - Commit and push the file.

2. **Add Repository Secrets**
   - Go to your repo → **Settings** → **Secrets and variables** → **Actions**.
   - Add `BACKEND_URL`: URL of your ReviewMate backend (e.g., `https://your-deployed-app.com`).
   - Add `GROQ_API_KEY`: Your Groq API key (if not using local embeddings).

3. **For Local Backends (Optional)**
   - Install ngrok: `npm install -g ngrok`
   - Run backend: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
   - Tunnel: `ngrok http 8000` (get public URL)
   - Set `BACKEND_URL` to ngrok URL.

4. **Test Setup**
   - Create a test PR in your repo.
   - Wait for workflow to run (check **Actions** tab).
   - AI analysis comment should appear on the PR.

### Configuration Options

- Edit workflow file to customize (e.g., disable agents, change triggers).
- For drafts/bots, add labels to skip analysis.

### Troubleshooting

- **Workflow Fails**: Check secrets and backend accessibility.
- **No Comments**: Verify GITHUB_TOKEN permissions.
- **Large PRs**: Analysis may timeout; split into smaller reviews.

### Example: Setting Up guanw/InterviewMate

1. **Expose Backend**:

   ```bash
   npm install -g ngrok
   source venv/bin/activate
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   # In new terminal: ngrok http 8000
   # Note the https://xxxxx.ngrok.io URL
   ```

2. **Copy Workflow**:
   - In https://github.com/guanw/InterviewMate, create `.github/workflows/pull_request_review.yml`
   - Copy content from ReviewMate's `.github/workflows/pull_request_review.yml`

3. **Add Secrets**:
   - Repo Settings → Secrets → Actions
   - `BACKEND_URL`: `https://your-ngrok-url.ngrok.io`
   - `GROQ_API_KEY`: Your key

4. **Test with PR #2**:
   - Push workflow, then update https://github.com/guanw/InterviewMate/pull/2
   - AI comment will appear automatically.

## Testing

```bash
python -m pytest tests/ -v
```
