# mcp-release-notifier

> An agentic pipeline that listens to GitHub releases, generates professional release notes with AI, and delivers a PDF to Discord — built with MCP, FastAPI, and the Claude API.

---

## Table of Contents

- [What is MCP?](#what-is-mcp)
- [Project Architecture](#project-architecture)
- [Requirements](#requirements)
- [Setup](#setup)
- [Project Structure](#project-structure)
- [Part 1 — MCP Server](#part-1--mcp-server)
- [Part 2 — Testing with MCP Inspector](#part-2--testing-with-mcp-inspector)
- [Part 3 — MCP Client](#part-3--mcp-client)
- [Part 4 — Client Test](#part-4--client-test)
- [Part 5 — FastAPI Webhook](#part-5--fastapi-webhook)
- [Part 6 — Cloudflared](#part-6--cloudflared)
- [Part 7 — GitHub Webhook](#part-7--github-webhook)
- [Part 8 — Full Pipeline](#part-8--full-pipeline)
- [Part 9 — Discord Setup](#part-9--discord-setup)
- [Part 10 — Send PDF to Discord](#part-10--send-pdf-to-discord)
- [Get in Touch](#get-in-touch)

---

## What is MCP?

The **Model Context Protocol (MCP)** is an open standard that defines how AI models communicate with external tools and data sources.

Think of it less like an API and more like **USB-C for AI** — a universal connector. Before MCP, every AI integration was a custom bridge written for one specific model or platform. With MCP, you build a server once and any MCP-compatible client (Claude Desktop, Cursor, your own app) can connect to it.

MCP exposes three primitives:

| Primitive | Analogy | Description |
|---|---|---|
| **Tool** | POST request | An action with side effects (generate PDF, send message) |
| **Resource** | GET request | Read-only data source (files, database records) |
| **Prompt** | Template | Reusable message templates for LLM interactions |

This project uses all three.

[↑ Back to Table of Contents](#table-of-contents)

---

## Project Architecture

```
GitHub Release
      │
      ▼
  Webhook (FastAPI + Cloudflared)
      │
      ▼
  Claude API  ──►  MCP Client  ──►  MCP Server
                                        │
                              ┌─────────┴─────────┐
                              ▼                   ▼
                         create_pdf          send_to_discord
                              │
                              ▼
                        PDF → Discord
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Requirements

- Python 3.10+
- A GitHub account
- A Discord server (you control)
- An Anthropic API key → [console.anthropic.com](https://console.anthropic.com)

[↑ Back to Table of Contents](#table-of-contents)

---

## Setup

> **Note on tooling:** I'm using `pip` throughout this project for simplicity and accessibility. The MCP ecosystem recommends `uv` (a faster Python package manager), but if you're not familiar with it yet, `pip` works perfectly here. Feel free to switch to `uv` if you prefer.

### 1. Clone the repository

```bash
git clone https://github.com/hasff/mcp-release-notifier.git
cd mcp-release-notifier
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Project Structure

```
mcp-release-notifier/
├── A_MCP_Server/
├── B_MCP_Client/
├── C_Webhook/
├── D_Pipeline/
├── E_Discord/
├── assets/
└── README.md
```

> ⚠️ Each part folder will be detailed as the project progresses.

[↑ Back to Table of Contents](#table-of-contents)

---

## Part 1 — MCP Server

> **What you'll learn:** How to create an MCP server with FastMCP, expose Tools, a Resource, and a Prompt.

### Theory

*(coming soon)*

### Code walkthrough

## 1. Install dependencies

```bash
pip install "mcp[cli]" reportlab
```

*(coming soon)*


[↑ Back to Table of Contents](#table-of-contents)

---

## Part 2 — Testing with MCP Inspector

> **What you'll learn:** How to use the MCP Inspector to test your server — call Tools, read Resources, and invoke Prompts manually.

### What is the MCP Inspector?

The MCP Inspector is an official browser-based UI that lets you interact with any MCP server without writing a client. It's the fastest way to verify your server works before wiring it to anything else.

### Run it

```bash
cd A_MCP_Server
mcp dev server.py
```

Open the URL shown in the terminal (usually `http://localhost:5173`).

### What to test

1. **Resources** → click `releases://latest` → verify the mock payload loads
2. **Prompts** → call `generate_release_notes` with a version and some changes
3. **Tools** → call `read_mock_release` → verify it returns the JSON
4. **Tools** → call `create_pdf` with fake data → verify a PDF appears in `output/`

*(screenshots coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

## Part 3 — MCP Client

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

## Part 4 — Client Test

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

## Part 5 — FastAPI Webhook

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

## Part 6 — Cloudflared

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

## Part 7 — GitHub Webhook

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

## Part 8 — Full Pipeline

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

## Part 9 — Discord Setup

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

## Part 10 — Send PDF to Discord

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

## Get in Touch
📩 Contact: hugoferro.business(at)gmail.com

🔗 [LinkedIn](https://www.linkedin.com/in/hugo-ferro-1434b414/)

[↑ Back to Table of Contents](#table-of-contents)

