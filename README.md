# mcp-release-notifier

> An agentic pipeline that listens to GitHub releases, generates professional release notes with AI, and delivers a PDF to Discord — built with MCP, FastAPI, and the Claude API.

---

⚠️ **Heads up**

This is a personal learning project — not an official Anthropic or MCP resource.
It may contain errors, simplifications, or opinionated choices made for clarity over correctness.
Think of it as a **warm-up project**: a hands-on way to get comfortable with MCP before tackling the recommended courses at the end of this README.

---

## Table of Contents

- [What is MCP?](#what-is-mcp)
- [Project Architecture](#project-architecture)
- [Requirements](#requirements)
- [Setup](#setup)
- [Project Structure](#project-structure)
- [Part 01 — 🖥️ MCP Server Setup](#part-1)
- [Part 02 — 🖥️🔧 Adding Tools](#part-2)
- [Part 03 — 🖥️🔧🔍 Testing Tools](#part-3)
- [Part 04 — 🖥️📚 Adding Resources](#part-4)
- [Part 05 — 🖥️📚🔍 Testing Resources](#part-5)
- [Part 06 — 🖥️✍️ Adding Prompts](#part-6)
- [Part 07 — 🖥️✍️🔍 Testing Prompts](#part-7)
- [Part 08 — 🔌 MCP Client Setup](#part-8)
- [Part 09 — 🔌🔍 Testing the Client](#part-9)
- [Part 10 — ⚡ FastAPI Webhook](#part-10)
- [Part 11 — 🌐 Cloudflared](#part-11)
- [Part 12 — 🐙 GitHub Webhook](#part-12)
- [Part 13 — 🔗 Full Pipeline](#part-13)
- [Part 14 — 🎮 Discord Setup](#part-14)
- [Part 15 — 📤 Sending the PDF](#part-15)
- [Next Steps & Resources](#next-steps--resources)
- [Get in Touch](#get-in-touch)

---

## What is MCP?

Imagine an AI as a person locked in a dark room. They can think, reason, and answer questions — but only based on what they already know, plus the context of the current conversation. No internet, no smartphone, no real-time data. *Just memory — their training data and the context they've been given.*

**MCP opens the door.**

**Before MCP**, connecting an AI to an external tool or data source meant writing custom code every time — fragile integrations that broke whenever a third-party service changed.

**MCP standardises that connection layer.**

If you're building an app and want to add AI capabilities that reach beyond the model itself — external tools, live data, third-party services — it can be up and running in minutes, not days.

**A practical example:**

❌ **Without MCP:** GitHub has a Web API with hundreds of actions. If you want your app to interact with GitHub via AI, you write custom integration code. If you have a second app that also needs GitHub, you write it again. And if GitHub changes or deprecates an endpoint — both apps break.

✅ **With MCP:** GitHub exposes an MCP Server. Your app connects to it, asks *"what can you do?"*, gets the list of available tools, feeds them to the AI model, and the model figures out how to use them. 💡 One protocol. Any app. Any model. Cool right?! 😎

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
🚨🚨🚨
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
> All examples in this project are built and tested with `pip` — not `uv`.

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
🚨🚨🚨
``` 
mcp-release-notifier/
├── MCP_Server/
|   ├── server_v1.py   ← Part 01: bare server
|   ├── server_v2.py   ← Part 02 and 03: + tools
|   ├── server_v3.py   ← Part 04 and 05: + resources  
|   ├── server_v4.py   ← Part 06 and 07: + prompts
|   └── release_data/
├── MCP_Client/
├── Webhook/
├── Pipeline/
├── Discord/
├── assets/
└── README.md
```

> ⚠️ Each part folder will be detailed as the project progresses.

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-1"></a>
## Part 01 — 🖥️ MCP Server Setup

> **What you'll learn:** How to scaffold a minimal MCP server — valid, runnable, but intentionally empty.

---

### Theory

MCP follows a **client-server architecture**:

- The **MCP Server** exposes capabilities — tools, resources, and prompts.
- The **MCP Client** connects to the server, discovers what's available, and exposes those capabilities to the AI model — which then decides how to use them.

Think of the server as a **capability provider**: it doesn't decide when or how its tools are used — it just makes them available. The intelligence lives on the client side.

> 💡 **In practice**, most developers interact with MCP as **clients** — connecting to servers that already exist (GitHub, Notion, Slack...). Building your own server is less common, and typically you'd focus on one side or the other. In this project, we build both — but that's intentional: the goal is to understand the full picture, not to model a production setup.

🚨🚨🚨
In this project, our server will eventually expose two tools (`read_last_release` and `create_pdf`), two resources, and one prompt. We also plan to consume an **external MCP server** (e.g. GitHub) as a client — but that part is still being designed. But first — let's get the skeleton running.
🚨🚨🚨

---

### Install dependencies

```bash
pip install "mcp[cli]"
```

> ⚠️ **`mcp` vs `fastmcp` — important distinction:**
> - `mcp` → official package, **Author: Anthropic, PBC** → [pypi.org/project/mcp](https://pypi.org/project/mcp)
> - `fastmcp` → third-party package, **Author: Jeremiah Lowin / Prefect** → [pypi.org/project/fastmcp](https://pypi.org/project/fastmcp)
>
> Despite the similar name, they are maintained by completely different teams. Having both installed can cause conflicts. **This project uses `mcp` only** — `FastMCP` is simply a class exposed inside the official Anthropic package (`mcp.server.fastmcp`).

> 💡 **Why `[cli]`?**
> The `[cli]` extra installs additional tools needed to run and inspect your server locally — including the **MCP Inspector**, which we'll use in Part 03. Without it, you'd have the core library but none of the dev tooling.

---

### Code walkthrough

> 📄 **File:** `MCP_Server/server_v1.py`
```python
# 1 — Import
from mcp.server.fastmcp import FastMCP

# 2 — Create server instance
mcp = FastMCP("release-notifier")

# TODO

# 3 — Run
if __name__ == "__main__":
    mcp.run()
```

**# 1 — Import:**
Imports the `FastMCP` class from the official `mcp` package. This class handles all the MCP protocol boilerplate — you just define tools, resources, and prompts on top of it.

**# 2 — Create server instance:**
Creates your server instance. The string `"release-notifier"` is the server name — it's what clients see when they connect and ask *"what server am I talking to?"*.

**# 3 — Run:**
Starts the server. By default, it uses **stdio transport** — the server communicates via standard input/output, which means the MCP client and the MCP server run on the **same machine**.

> 💡 **Transport is just a detail.** MCP is **transport-agnostic** — the core concepts (tools, resources, prompts) work the same regardless of whether communication happens over stdio (local) or HTTP (remote). The transport choice may affect some low-level behaviour, but that's beyond the scope of this project. Here we use stdio.
>
> 🐇 **Want to go deeper?** Ask an AI: *"What is the difference between HTTP+SSE and StreamableHTTP in MCP, and why might you need to disable notifications in HTTP-based transports?"*
---

### Run it

Curious to see if it's already alive? Run this in your terminal:

```bash
mcp dev MCP_Server/server_v1.py
```

You should see something like this:

![Connect button](assets/part_01/screenshot_terminal.jpg)

Now open the URL shown in the terminal. You'll land on the MCP Inspector:

![Connect button](assets/part_01/screenshot_browser.jpg)

Click **Connect** to establish the connection with your server.

> ⚠️ **Command field:** The Inspector pre-fills this based on your system.
> - Windows: typically `py`
> - macOS / Linux: typically `python` or `python3`
>
> The **Arguments** field should contain the path to your server file (e.g. `MCP_Server/server_v1.py`).

![Connect button](assets/part_01/screenshot_connect_button.jpg)

Once connected — no tools, no resources, nothing yet. But the server is alive and responding. ✅

![Connect button](assets/part_01/screenshot_connected.jpg)

❎ When you're done, press `Ctrl + C` in the terminal to stop the server.

---

### 🎮 Quiz

*(coming soon)*

---

> 💡 **MCP Curiosity**
> MCP was publicly released by Anthropic in November 2024 — but it was designed from the start as an **open standard**, not an Anthropic-exclusive protocol. Any AI model, any client, any server can implement it. The goal is interoperability, not lock-in.

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-2"></a>
## Part 02 — 🖥️🔧 Adding Tools

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-3"></a>
## Part 03 — 🖥️🔧🔍 Testing Tools

> **What you'll learn:** How to use the MCP Inspector to test your server — call Tools manually and verify their output.

### What is the MCP Inspector?

The MCP Inspector is an official browser-based UI that lets you interact with any MCP server without writing a client. It's the fastest way to verify your server works before wiring it to anything else.

### Run it

```bash
mcp dev MCP_Server/server.py
```

Open the URL shown in the terminal (usually `http://localhost:5173`).

### What to test

1. **Tools** → call `read_last_release` → verify it returns the JSON
2. **Tools** → call `create_pdf` with fake data → verify a PDF appears in `output/`

*(screenshots coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-4"></a>
## Part 04 — 🖥️📚 Adding Resources

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-5"></a>
## Part 05 — 🖥️📚🔍 Testing Resources

> ⚠️ **MCP Inspector behaviour:** After calling a template resource (`releases://by/{id}`),
> the Inspector may return cached results for subsequent static resource calls (`releases://latest`).
> Refresh the page to reset.

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-6"></a>
## Part 06 — 🖥️✍️ Adding Prompts

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-7"></a>
## Part 07 — 🖥️✍️🔍 Testing Prompts

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-8"></a>
## Part 08 — 🔌 MCP Client Setup

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-9"></a>
## Part 09 — 🔌🔍 Testing the Client

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-10"></a>
## Part 10 — ⚡ FastAPI Webhook

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-11"></a>
## Part 11 — 🌐 Cloudflared

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-12"></a>
## Part 12 — 🐙 GitHub Webhook

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-13"></a>
## Part 13 — 🔗 Full Pipeline

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-14"></a>
## Part 14 — 🎮 Discord Setup

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

<a name="part-15"></a>
## Part 15 — 📤 Sending the PDF

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---

## Next Steps & Resources

Want to go deeper? Here are the resources that inspired and complement this project.

**Model Context Protocol**
- 🤗 [MCP Course — Hugging Face](https://huggingface.co/learn/mcp-course/unit0/introduction) — *the pipeline in this project was inspired by this course*
- 🟠 [Introduction to Model Context Protocol — Anthropic](https://anthropic.skilljar.com/introduction-to-model-context-protocol)
- 🟠 [Model Context Protocol: Advanced Topics — Anthropic](https://anthropic.skilljar.com/model-context-protocol-advanced-topics)

**PDF Generation**
- 🐍 [Python PDF Generation: From Beginner to Winner (ReportLab)](https://www.udemy.com/course/python-reportlab-from-beginner-to-winner/?referralCode=3B927E883D2E868CF221)

[↑ Back to Table of Contents](#table-of-contents)

---

## Get in Touch
📩 Contact: hugoferro.business (at) gmail.com

🔗 [LinkedIn](https://www.linkedin.com/in/hugo-ferro-1434b414/)

[↑ Back to Table of Contents](#table-of-contents)
