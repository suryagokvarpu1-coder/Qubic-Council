# Vibe-Coding Consensus Engine - Walkthrough

## How to Run

### Prerequisite
Ensure you have Python 3.11+ and Node.js installed.

### 1. Start the Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
*The API will be available at http://localhost:8000*

### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
* Access the UI at the URL provided (usually http://localhost:5173)*

## Example Execution

### Input
**User Prompt**: "I need a scalable web app. What stack should I use?"

### System Flow
1.  **Normalization**: Detects intent `build_application`. Infers `web` platform.
2.  **Constraints**: Locks `platform=web` to prevent mobile-only suggestions.
3.  **Parallel Execution**:
    -   *Model A (GPT-4)*: Suggests "React + Node.js".
    -   *Model B (Gemini)*: Suggests "Next.js for scalability".
    -   *Model C (Claude)*: Suggests "Vue for simplicity".
4.  **Claim Extraction**:
    -   Split texts into atomic claims like "React is a good library", "Next.js offers scalability".
5.  **Agreement**:
    -   All models agree on "Javascript-based Frontend".
    -   Conflict detected: React vs Vue (Preferences).
6.  **Scoring**:
    -   "Javascript Frontend": Score 0.95 (High Agreement).
    -   "Use Vue": Score 0.4 (Outlier).
7.  **Consensus Synthesis**:
    -   "The consensus recommends a Javascript-based stack (React/Next.js) for scalability. Vue is an alternative but less emphasized for this specific constraint set."

### Final Output (UI)
-   **Consensus Badge**: 90% Confidence
-   **Answer**: "The consensus suggests using a modern frontend framework like React, Next.js, or Vue.js..."
-   **Uncertain Areas**: "Specific choice of framework (React vs Vue) is disputed"
