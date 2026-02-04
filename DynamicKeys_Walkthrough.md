# Feature Walkthrough: Universal API Key & Provider Auto-Detection

## Overview
The "Universal API Key" feature allows you to input a single API key from any supported provider (OpenAI, Groq, OpenRouter), and the system will automatically:
1.  **Detect** the provider based on the key format.
2.  **Configure** the backend to use that provider's models.
3.  **Adapt** the request/response logic to match the provider's capabilities.

## How to Use
1.  Open the application (`http://localhost:8000`).
2.  Click the **Configuration Gear** or **COUNCIL_CONFIG** button in the top right to open the Sidebar.
3.  Scroll to the bottom of the Sidebar to the **UNIVERSAL API KEY** section.
4.  Paste your API key (e.g., `sk-...`, `gsk_...`, `sk-or-...`).
5.  Click **CONNECT & DETECT**.

## Supported Providers & Formats
| Provider | Key Format | Detection Logic | Available Models |
| :--- | :--- | :--- | :--- |
| **OpenAI** | `sk-...` | Starts with `sk-` | GPT-4o, GPT-4 Turbo, GPT-3.5 |
| **Groq** | `gsk_...` | Starts with `gsk_` | Llama 3.3 70B, Llama 3 70B, Mixtral |
| **OpenRouter** | `sk-or-...` | Starts with `sk-or-` | GPT-4o, Claude 3.5 Sonnet, Gemini 2.0 |
| **Anthropic** | `sk-ant-...` | Starts with `sk-ant-` | *(Mapped to OpenRouter fallback)* |

## Auto-Reconfiguration
When you switch keys, the system instantly reconfigures:
-   **Model List**: The backend uses the provider's default model list.
-   **Execution Layer**: The `AntigravityEngine` switches to the appropriate client (OpenAI SDK or OpenRouter specific headers).
-   **Visual Feedback**: The sidebar shows a green "CONNECTED: [PROVIDER]" indicator.

## Troubleshooting
-   **"Unknown Provider"**: Ensure your key has no extra spaces. If the format is new, try using an OpenRouter key instead.
-   **"Connection Failed"**: Check your internet connection and verify the key is active.
-   **Auth Errors**: If using an Anthropic key, note that this version prioritizes OpenRouter for Anthropic models. We recommend using an OpenRouter key if you want access to Claude 3.5 Sonnet alongside other models.
