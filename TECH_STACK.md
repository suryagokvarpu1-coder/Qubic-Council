# 🛠️ Technology Stack

## 🎨 Frontend (User Interface)
The current frontend is built with **Vanilla technologies** for maximum performance and visual control.

- **Core**: HTML5, Vanilla JavaScript (ES6+).
- **Styling**: 
  - **Tailwind CSS** (via CDN) for utility-first styling.
  - **Custom CSS3** for advanced animations (3D transforms, keyframes) and glassmorphism.
- **Graphics**: HTML5 `<canvas>` for the interactive geometric background (`mainpage.html`).
- **Fonts**: Google Fonts
  - *Space Grotesk* (Loading UI)
  - *Plus Jakarta Sans* (Main Headings)
  - *JetBrains Mono* (Technical/Data elements)

## ⚙️ Backend (Server & Logic)
A high-performance asynchronous Python backend.

- **Framework**: **FastAPI** (Modern, fast web framework).
- **Server**: **Uvicorn** (ASGI server).
- **Language**: Python 3.x.
- **Core Libraries**:
  - `pydantic`: Data validation and settings management.
  - `networkx`: Graph data structures for the consensus engine.
  - `numpy` & `scikit-learn`: Data analysis and clustering algorithms.
  - `openai`: Official SDK (used as a client for both OpenRouter and Groq).

## 🧠 AI & LLM Infrastructure (The Council)
The core "Vibe-Coding Consensus Engine" orchestrates multiple AI models.

- **Orchestrator**: Custom Graph-based Engine (`AntigravityEngine`).
- **API Gateways**:
  - **OpenRouter**: Unified access to top-tier models.
  - **Groq**: Ultra-low latency inference.
- **Active Models**:
  1. **GPT-4o** (OpenAI) - *Chairman / Synthesis*
  2. **Claude 3.5 Sonnet** (Anthropic) - *Reasoning / Coding*
  3. **Gemini 2.0 Flash** (Google) - *Speed / Context*
  4. **Llama 3.3 70B** (Meta via Groq) - *High-speed Open Source*

## 🚀 Deployment & DevOps
- **Local Config**: `.env` file for API keys.
- **Static Serving**: FastAPI `StaticFiles` serving the HTML frontend directly.
