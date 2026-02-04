# Vibe-Coding Consensus Engine

A multi-LLM consensus platform that orchestrates parallel execution, peer review, and synthesis to provide authoritative answers.

## ✨ Features

- **Universal API Key**: Supports OpenAI, Groq, and OpenRouter keys with auto-detection
- **Dynamic Council**: Configure 1-4 models for parallel execution
- **8-Layer Graph**: Normalization, Constraint Locking, Execution, Extraction, Peer Review, Agreement, Scoring, Synthesis
- **Live UI**: Real-time visualization of the consensus process
- **Conversation Persistence**: Save and load previous queries

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, AsyncIO
- **Frontend**: HTML5, Vanilla JS, TailwindCSS
- **AI**: OpenAI SDK, OpenRouter, Groq

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <repo-url>
cd test-llm-council/backend
pip install -r requirements.txt
```

### 2. Run the Server

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Open the Application

Navigate to: **http://localhost:8000**

The loading page will automatically redirect you to the main application.

## 🔑 Configuration

### Setting Up API Keys

1. Click the **gear icon (⚙)** or **COUNCIL_CONFIG** button in the top-right
2. Enter your API key in the **UNIVERSAL API KEY** field
3. Click **CONNECT & DETECT**

### Supported API Keys

| Provider | Key Format | Get Key |
|----------|------------|---------|
| OpenRouter | `sk-or-v1-...` | [openrouter.ai/keys](https://openrouter.ai/keys) |
| OpenAI | `sk-...` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Groq | `gsk_...` | [console.groq.com](https://console.groq.com/keys) |

> **Tip**: OpenRouter gives you access to multiple models (GPT-4o, Claude, Gemini) with a single key!

## 📖 Documentation

- **[API Documentation](docs/API_DOCUMENTATION.md)** - Endpoint references, request/response schemas
- **[Platform Documentation](docs/PLATFORM_DOCUMENTATION.md)** - Architecture, data flow, extending the system

## 🧪 Running Tests

```bash
cd backend
pip install pytest pytest-asyncio
python -m pytest tests/ -v
```

## 📁 Project Structure

```
test-llm-council/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app & routes
│   │   ├── models.py        # Pydantic data models
│   │   ├── engine/          # Core consensus logic
│   │   └── config/          # Settings management
│   ├── static/              # HTML frontend
│   ├── tests/               # Test suite
│   └── requirements.txt
├── frontend/                # React alternative frontend
├── docs/                    # Documentation
└── README.md
```

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Loading page |
| `/mainpage` | GET | Main application |
| `/api/status` | GET | Health check |
| `/run` | POST | Execute consensus query |
| `/settings/keys` | POST | Update API keys |
| `/conversations` | GET | List saved conversations |
| `/conversations/{id}` | GET | Get specific conversation |

## 💡 How It Works

1. **Normalization**: Your query is analyzed to extract intent, domain, and constraints
2. **Parallel Execution**: Multiple LLMs process your query simultaneously
3. **Claim Extraction**: Each response is broken down into atomic, testable claims
4. **Peer Review**: Models anonymously review and score each other
5. **Agreement Detection**: Similar claims are grouped into clusters
6. **Confidence Scoring**: Each cluster gets a confidence score based on agreement
7. **Synthesis**: A "Chairman" model synthesizes the final authoritative answer

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Submit a pull request

## 📄 License

MIT License
