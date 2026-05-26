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

#### ⚡ Quick Navigation: [⬅️ Table of Contents](#table-of-contents) | [Project Architecture ➡️](#project-architecture)


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

### Watch this 10 minute video from IBM - MCP vs API: Simplifying AI Agent Integration with External Data
[![Watch from IBM - MCP vs API: Simplifying AI Agent Integration with External Data](https://img.youtube.com/vi/7j1t3UZA1TY/maxresdefault.jpg)](https://youtu.be/7j1t3UZA1TY)

[↑ Back to Table of Contents](#table-of-contents)

---


## Project Architecture

#### ⚡ Quick Navigation: [⬅️ What is MCP?](#what-is-mcp) | [Requirements ➡️](#requirements)


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

#### ⚡ Quick Navigation: [⬅️ Project Architecture](#project-architecture) | [Setup ➡️](#setup)


- Python 3.10+
- A GitHub account
- A Discord server (you control)
- An Anthropic API key → [console.anthropic.com](https://console.anthropic.com)

[↑ Back to Table of Contents](#table-of-contents)

---


## Setup

#### ⚡ Quick Navigation: [⬅️ Requirements](#requirements) | [Project Structure ➡️](#project-structure)



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

#### ⚡ Quick Navigation: [⬅️ Setup](#setup) | [Part 01 ➡️](#part-1)


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

#### ⚡ Quick Navigation: [⬅️ Project Structure](#project-structure) | [Part 02 — 🖥️🔧 Adding Tools ➡️](#part-2)


> 📒 **What you'll learn:** How to scaffold a minimal MCP server — valid, runnable, but intentionally empty.

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

#### ⚡ Quick Navigation: [⬅️ Part 01 — 🖥️ MCP Server Setup](#part-1) | [Part 03 — 🖥️🔧🔍 Testing Tools ➡️](#part-3)

> 📒 **What you'll learn:** How to define and register tools in an MCP server — and why the registration step matters.

---


### Theory

In MCP, a **Tool** is a callable function the AI can invoke — something with side effects, like reading a file or generating a PDF.

But just defining a Python function isn't enough. The MCP server needs to know the function exists. That registration step is what makes the difference between a plain Python function and an MCP tool.

In this part we'll add two tools to our server:

- `read_last_release` — reads the latest release JSON from `release_data/`
- `create_pdf` — generates a PDF and saves it to `output/`

The folder structure looks like this:

![Input and output folders](assets/part_02/screenshot_input_output_folders.jpg)

---


### Install dependencies

```bash
pip install reportlab
```

> 💡 **What is ReportLab?**
> ReportLab is a Python library for generating PDFs programmatically. Our `create_pdf` tool will use it to build a structured PDF from the release notes data.

---


### Code walkthrough

> 📄 **File:** `MCP_Server/server_v2.py`

#### Step 1 — Imports

```python
# 1 — Standard library
import json
from pathlib import Path
from datetime import datetime

# 2 — MCP
from mcp.server.fastmcp import FastMCP

# 3 — ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
```

**# 1 — Standard library:**
`json` handles reading the release JSON files. `Path` gives us a clean, cross-platform way to work with file paths. `datetime` is used to timestamp the generated PDF filenames.

**# 2 — MCP:**
Already covered in Part 01 — this is the `FastMCP` class that powers our server.

**# 3 — ReportLab:**
`A4` defines the page size. `SimpleDocTemplate` is the PDF document builder. `Paragraph` and `Spacer` are layout elements — text blocks and vertical spacing. `getSampleStyleSheet` provides a set of pre-built text styles (Title, Heading, Normal).

---


#### Step 2 — Project paths

```python
# ─────────────────────────────────────────────
# ⚙️ CONFIGURATION
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
RELEASE_DATA_DIR = BASE_DIR / "release_data"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
```

`BASE_DIR` is the directory where `server_v2.py` lives. Everything else is relative to it — `release_data/` is where the input JSON files come from, and `output/` is where generated PDFs will be saved. `OUTPUT_DIR.mkdir(exist_ok=True)` ensures the folder is created automatically if it doesn't exist yet.

---


#### Step 3 — Define the functions (plain Python)

Before registering anything with MCP, let's define the two functions as plain Python:

```python
# read_last_release — reads the latest JSON from release_data/
def read_last_release() -> dict: ...

# create_pdf — generates a PDF and saves it to output/
def create_pdf(version: str, repo_name: str, release_notes: str, published_at: str) -> dict: ...
```

> ⚠️ At this point these are just regular Python functions. The MCP server has no idea they exist — nothing has been registered yet. We'll fix that in the next step.

> 📄 **Full implementation:** `MCP_Server/server_v2.py`

---


#### Step 4 — Register the tools with MCP

To expose a function as an MCP tool, we add the `@mcp.tool()` decorator:

```python
# ─────────────────────────────────────────────
# 🔧 TOOL 1 — read last release
# ─────────────────────────────────────────────
@mcp.tool()
def read_last_release() -> dict:
    """Reads the most recent release payload from release_data/."""
    ...

# ─────────────────────────────────────────────
# 🔧 TOOL 2 — create PDF
# ─────────────────────────────────────────────
@mcp.tool()
def create_pdf(version: str, repo_name: str, release_notes: str, published_at: str) -> dict:
    """
    Generates a PDF with the release notes.
    Returns the output filename.

    Args:
        version: The release version tag (e.g. 'v1.2.0')
        repo_name: The repository name (e.g. 'mcp-release-notifier')
        release_notes: The full release notes text
        published_at: ISO 8601 timestamp of the release
    """
    ...
```

Three things to note here:

**`@mcp.tool()`** — `mcp` is not a generic name. It refers to the server instance we created in Part 01: `mcp = FastMCP("release-notifier")`. The decorator registers the function with that specific server.

**`@mcp.tool()` vs `@mcp.tool(description="...")`** — Both work. The docstring approach (used here) is more Pythonic and keeps the description close to the code. Passing `description=` directly in the decorator is an alternative — pick the one that fits your style.

**Docstrings matter for AI** — The description at the top of each function, and the `Args:` block for each parameter, are not just for human readers. FastMCP exposes them to the AI model so it knows what each tool does and how to call it correctly. The clearer the description, the better the model performs.

---


### 🎮 Quiz

*(coming soon)*

---


> 💡 **MCP Curiosity**
> Every MCP server publishes a machine-readable catalog — `tools/list`, `resources/list`, `prompts/list`. This means an AI agent can discover new capabilities at runtime without any code changes on the client side.

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-3"></a>
## Part 03 — 🖥️🔧🔍 Testing Tools

#### ⚡ Quick Navigation: [⬅️ Part 02 — 🖥️🔧 Adding Tools](#part-2) | [Part 04 — 🖥️📚 Adding Resources ➡️](#part-4)

> 📒 **What you'll learn:** How to use the MCP Inspector to test your tools — call them manually, inspect their output, and verify the full flow before wiring anything to a client.

---


### What is the MCP Inspector?

The MCP Inspector is an official browser-based UI that lets you interact with any MCP server without writing a client. Think of it as **Postman for MCP** — it's the fastest way to verify your server works before connecting it to anything else.

---


### Run it

```bash
mcp dev MCP_Server/server_v2.py
```

You should see something like this in your terminal:

![Terminal running mcp dev](assets/part_03/screenshot_terminal.jpg)

Open the URL shown in the terminal (in this case is `http://localhost:6274`).

---


### Connect to your server

On the connection screen, verify the pre-filled fields and click **Connect**:

- **1) Command** — `py` on Windows, `python` or `python3` on macOS/Linux
- **2) Arguments** — path to your server file: `MCP_Server/server_v2.py`
- **3) Connect** — click to establish the connection

![Connection screen](assets/part_03/screenshot_connect_button.jpg)

---


### Navigate to Tools

Once connected, click **Tools** in the top navigation bar.

![Tools button highlighted](assets/part_03/screenshot_connected_tools_btn.jpg)

Then click **List Tools** to fetch the tools registered on your server.

![List Tools button](assets/part_03/screenshot_connected_list_tools_btn.jpg)

You should now see both tools available — `read_last_release` and `create_pdf`.

![Available tools](assets/part_03/screenshot_connected_available_tools.jpg)

---


### Test 1 — `read_last_release`

Click **`read_last_release`** to select it.

This tool takes no parameters — just click **Run Tool**.

- **1) `read_last_release`** — select tool
- **2) Run Tool** — click to execute

![read_last_release selected](assets/part_03/screenshot_connected_read_last_release_1.jpg)

The result should be the JSON content of the latest file in `release_data/`:

![read_last_release result](assets/part_03/screenshot_connected_read_last_release_2.jpg)

```json
{
  "action": "published",
  "release": {
    "tag_name": "v1.2.6760",
    "name": "Release v1.2.6760",
    "body": "## What's Changed? \n- Fix login bug\n- Add dark mode\n- Improve performance",
    "published_at": "2025-05-23T10:00:00Z",
    "html_url": "https://github.com/user/repo/releases/tag/v1.2.0"
  },
  "repository": {
    "name": "mcp-release-notifier",
    "full_name": "user/mcp-release-notifier",
    "html_url": "https://github.com/user/mcp-release-notifier"
  }
}
```

✅ Tool working correctly.

---


### Test 2 — `create_pdf`

Click **`create_pdf`** to select it.

![create_pdf button](assets/part_03/screenshot_connected_create_pdf_1.jpg)

This tool requires four parameters. Fill them in with any test values:

| Parameter | Example value |
|---|---|
| `version` | `123` |
| `repo_name` | `my_repo/example` |
| `release_notes` | `This is a demo!` |
| `published_at` | `2026-05-26` |

Then click **Run Tool**.

![create_pdf parameters filled](assets/part_03/screenshot_connected_create_pdf_2.jpg)

You should see **Tool Result: Success** with the output path:

![create_pdf result](assets/part_03/screenshot_connected_create_pdf_3.jpg)

```json
{
  "success": true,
  "file": "release_123_20260526_145605.pdf",
  "path": "C:\\Users\\...\\MCP_Server\\output\\release_123_20260526_145605.pdf"
}
```

Open the `output/` folder in your project — the PDF should be there. Open it to confirm the content matches what you passed in:

![Output folder in VSCode](assets/part_03/screenshot_output_folder.jpg)

✅ Both tools verified end-to-end.

---


### What to keep in mind

> ⚠️ The MCP Inspector sends one tool call at a time — it's a manual testing environment, not an AI agent. In later parts, the AI client will chain these calls automatically based on the task.

❎ When you're done, press `Ctrl + C` in the terminal to stop the server.

---


### 🎮 Quiz

*(coming soon)*

---


> 💡 **MCP Curiosity**
> The MCP Inspector is itself an MCP client — it implements the full protocol to discover and call tools, just like your future AI-powered client will. The difference is that a human drives it here, not a model.

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-4"></a>
## Part 04 — 🖥️📚 Adding Resources

#### ⚡ Quick Navigation: [⬅️ Part 03 — 🖥️🔧🔍 Testing Tools](#part-3) | [Part 05 — 🖥️📚🔍 Testing Resources ➡️](#part-5)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-5"></a>
## Part 05 — 🖥️📚🔍 Testing Resources

#### ⚡ Quick Navigation: [⬅️ Part 04 — 🖥️📚 Adding Resources](#part-4) | [Part 06 — 🖥️✍️ Adding Prompts ➡️](#part-6)

> ⚠️ **MCP Inspector behaviour:** After calling a template resource (`releases://by/{id}`),
> the Inspector may return cached results for subsequent static resource calls (`releases://latest`).
> Refresh the page to reset.

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-6"></a>
## Part 06 — 🖥️✍️ Adding Prompts

#### ⚡ Quick Navigation: [⬅️ Part 05 — 🖥️📚🔍 Testing Resources](#part-5) | [Part 07 — 🖥️✍️🔍 Testing Prompts ➡️](#part-7)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-7"></a>
## Part 07 — 🖥️✍️🔍 Testing Prompts

#### ⚡ Quick Navigation: [⬅️ Part 06 — 🖥️✍️ Adding Prompts](#part-6) | [Part 08 — 🔌 MCP Client Setup ➡️](#part-8)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-8"></a>
## Part 08 — 🔌 MCP Client Setup

#### ⚡ Quick Navigation: [⬅️ Part 07 — 🖥️✍️🔍 Testing Prompts](#part-7) | [Part 09 — 🔌🔍 Testing the Client ➡️](#part-9)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-9"></a>
## Part 09 — 🔌🔍 Testing the Client

#### ⚡ Quick Navigation: [⬅️ Part 08 — 🔌 MCP Client Setup](#part-8) | [Part 10 — ⚡ FastAPI Webhook ➡️](#part-10)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-10"></a>
## Part 10 — ⚡ FastAPI Webhook

#### ⚡ Quick Navigation: [⬅️ Part 09 — 🔌🔍 Testing the Client](#part-9) | [Part 11 — 🌐 Cloudflared ➡️](#part-11)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-11"></a>
## Part 11 — 🌐 Cloudflared

#### ⚡ Quick Navigation: [⬅️ Part 10 — ⚡ FastAPI Webhook](#part-10) | [Part 12 — 🐙 GitHub Webhook ➡️](#part-12)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-12"></a>
## Part 12 — 🐙 GitHub Webhook

#### ⚡ Quick Navigation: [⬅️ Part 11 — 🌐 Cloudflared](#part-11) | [Part 13 — 🔗 Full Pipeline ➡️](#part-13)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-13"></a>
## Part 13 — 🔗 Full Pipeline

#### ⚡ Quick Navigation: [⬅️ Part 12 — 🐙 GitHub Webhook](#part-12) | [Part 14 — 🎮 Discord Setup ➡️](#part-14)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-14"></a>
## Part 14 — 🎮 Discord Setup

#### ⚡ Quick Navigation: [⬅️ Part 13 — 🔗 Full Pipeline](#part-13) | [Part 15 — 📤 Sending the PDF ➡️](#part-15)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-15"></a>
## Part 15 — 📤 Sending the PDF

#### ⚡ Quick Navigation: [⬅️ Part 14 — 🎮 Discord Setup](#part-14) | [Next Steps & Resources ➡️](#next-steps--resources)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


## Next Steps & Resources

#### ⚡ Quick Navigation: [⬅️ Part 15 — 📤 Sending the PDF](#part-15) | [Get in Touch ➡️](#get-in-touch)

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

#### ⚡ Quick Navigation: [⬅️ Next Steps & Resources](#next-steps--resources) | [⬆️ Back to Top](#mcp-release-notifier)


📩 Contact: hugoferro.business (at) gmail.com

🔗 [LinkedIn](https://www.linkedin.com/in/hugo-ferro-1434b414/)

[↑ Back to Table of Contents](#table-of-contents)

---


## By the way, did you hear about A2A?
#### Watch this 10 minute video from IBM - A2A vs MCP: AI Agent Communication Explained
[![Watch from IBM - A2A vs MCP: AI Agent Communication Explained](https://img.youtube.com/vi/BMDFPOyezH4/maxresdefault.jpg)](https://youtu.be/BMDFPOyezH4)

[↑ Back to Table of Contents](#table-of-contents)