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
- [Part 09 — 🔌🔧🔍 Testing Tools](#part-9)
- [Part 10 — 🔌📚🔍 Testing Resources](#part-10)
- [Part 11 — 🔌✍️🔍 Testing Prompts](#part-11)
- [Part 12 — 🔌🤖 The AI Pipeline](#part-12)
- [Part 13 — 🔌🚀 Running the Pipeline](#part-13)
- [Part 14 — ⚡ FastAPI Webhook](#part-14)
- [Part 15 — 🌐 Cloudflared](#part-15)
- [Part 16 — 🐙 GitHub Webhook](#part-16)
- [Part 17 — 🔗 Full Pipeline](#part-17)
- [Part 18 — 🎮 Discord Setup](#part-18)
- [Part 19 — 📤 Sending the PDF](#part-19)
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

<a name="part-1"></a>

---

# 🖥️ MCP Server
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

<a name="part-2"></a>

---

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

<a name="part-3"></a>

---

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

<a name="part-4"></a>

---

## Part 04 — 🖥️📚 Adding Resources

#### ⚡ Quick Navigation: [⬅️ Part 03 — 🖥️🔧🔍 Testing Tools](#part-3) | [Part 05 — 🖥️📚🔍 Testing Resources ➡️](#part-5)

> 📒 **What you'll learn:** How to define and register resources in an MCP server — the difference between static and template resources, how URIs work, and when to use `mime_type`.

---


### Theory

In MCP, a **Resource** is a read-only data source the AI (or a human) can read — something without side effects, like listing files or fetching a record.

The key distinction from Tools:

| | Tool | Resource |
|---|---|---|
| Analogy | POST request | GET request |
| Side effects | Yes | No |
| Use case | Do something | Read something |
| Example | `create_pdf` | `releases://list` |

Resources are registered with `@mcp.resource()` — the same pattern as `@mcp.tool()`.

---


### ⚠️ Important context for this project

> **Resources in this project exist for demonstration purposes only.**
>
> In our automated pipeline, the LLM will follow explicit tool-call instructions:
> `read_last_release()` → `create_pdf()`. Resources are not part of that flow.
>
> Where resources shine is in **ad-hoc, human-driven queries** — a developer asking
> *"what releases do we have?"* or *"show me the notes for release X"* — without
> triggering the full pipeline.

This is a deliberate design choice, not a gap. Tools handle the pipeline; resources handle exploration.

---


### URIs

Every resource is identified by a **URI** — a string that uniquely addresses it.

MCP URIs follow this pattern:

```
scheme://path
```

You define the scheme yourself. In this project we use `releases://`:

| URI | Type | Description |
|---|---|---|
| `releases://list` | Static | Fixed address, always the same resource |
| `releases://by/{id}` | Template | Dynamic address, `{id}` is a parameter |

> 💡 **URIs are not URLs.** They don't point to an HTTP endpoint — they're just identifiers within the MCP protocol. The scheme (`releases://`) is arbitrary; you define it when you register the resource.

---


### Static vs Template Resources

**Static resource** — fixed URI, content resolved dynamically at read time:
```python
@mcp.resource("releases://list", ...)
def list_releases() -> str: ...
```
The address never changes. The content can — every call re-reads the folder.

**Template resource** — URI with a `{parameter}`, resolved per request:
```python
@mcp.resource("releases://by/{id}", ...)
def get_release_by_id(id: str) -> str: ...
```
The `{id}` in the URI maps directly to the `id: str` parameter in the function. FastMCP handles the extraction automatically.

---


### mime_type

`mime_type` is metadata the server sends to the client so it knows how to interpret the content — the same principle as `Content-Type` in HTTP. **FastMCP** defaults to `text/plain` if omitted, but being explicit is good practice.

Common values:

| mime_type | When to use |
|---|---|
| `application/json` | Structured data |
| `text/plain` | Free text, logs, changelogs |
| `text/markdown` | Documentation, READMEs |
| `text/html` | Web content |

In this project:
- `releases://list` → `application/json` (returns a structured list)
- `releases://by/{id}` → `text/plain` (returns the release notes body as free text)

> 💡 **Note:** Unlike Tools, we pass `description` as a parameter directly in `@mcp.resource()` — not as a docstring. Both approaches are valid in FastMCP; for resources the decorator parameter keeps the metadata co-located with the URI and mime_type declaration, making it easier to read.

---


### Code walkthrough

> 📄 **File:** `MCP_Server/server_v3.py`

#### Resource 1 — Static resource

```python
# ─────────────────────────────────────────────
# 📚 RESOURCE 1 — static resource
# Lists all available release IDs from release_data (sorted, most recent last).
# Type: Static resource — fixed URI, dynamic content resolved at read time.
# ─────────────────────────────────────────────
@mcp.resource(
    "releases://list",
    description="Lists all available release IDs from release_data",
    mime_type="application/json"
)
def list_releases() -> str:
    files = sorted(RELEASE_DATA_DIR.glob("release_[0-9]*.json"))
    if not files:
        return json.dumps({"error": "No release files found in release_data"})
    ids = [f.stem for f in files]  # e.g. ["release_20260524_103042", ...]
    return json.dumps({"releases": ids, "count": len(ids)})
```
> ⚠️ **Production note:** Error handling is intentionally minimal to keep the focus on MCP concepts. In production you'd want proper exception handling and logging.

**`@mcp.resource("releases://list", ...)`** — registers a static resource at a fixed URI.

**`description=`** — passed directly as a decorator parameter (instead of a docstring). 
The client uses this to understand what the resource provides — visible in the MCP Inspector 
and in any application that calls `resources/list`.

**`mime_type="application/json"`** — tells the client the response is structured JSON.

**`f.stem`** — returns the filename without extension. This gives us exactly the `id` format that Resource 2 expects: `release_20260524_103042`.

---


#### Resource 2 — Template resource

```python
# ─────────────────────────────────────────────
# 📚 RESOURCE 2 — template resource
# Returns a specific release notes by id (e.g. releases://by/release_20260524_103042).
# Type: Template resource — URI with parameter {id}, resolved dynamically per request.
# ─────────────────────────────────────────────
@mcp.resource(
    "releases://by/{id}",
    description="Returns the release notes body by id as plain text",
    mime_type="text/plain"
)
def get_release_by_id(id: str) -> str:
    path = RELEASE_DATA_DIR / f"{id}.json"
    if not path.exists():
        return f"{id}.json not found in release_data"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["release"]["body"]
```
> ⚠️ **Production note:** Error handling is intentionally minimal to keep the focus on MCP concepts. In production you'd want proper exception handling and logging.

**`"releases://by/{id}"`** — the `{id}` placeholder makes this a template resource. FastMCP extracts the value from the URI and passes it to `id: str` automatically.

**`mime_type="text/plain"`** — the function returns only `data["release"]["body"]`, which is free text (e.g. `"## What's Changed?\n- Fix login bug\n..."`). Genuinely plain text, no JSON wrapper.

**The two resources are designed to chain naturally:**
```
releases://list            → discover available IDs
releases://by/{id}         → fetch the notes for a specific one
```

---


### 🎮 Quiz

*(coming soon)*

---


> 💡 **MCP Curiosity**
> Resources are exposed via `resources/list` and `resources/read` in the MCP protocol. A client can call `resources/list` at any time to discover what's available — no hardcoding needed. This is the same discovery mechanism used by Tools (`tools/list`) and Prompts (`prompts/list`).

[↑ Back to Table of Contents](#table-of-contents)

<a name="part-5"></a>

---

## Part 05 — 🖥️📚🔍 Testing Resources

#### ⚡ Quick Navigation: [⬅️ Part 04 — 🖥️📚 Adding Resources](#part-4) | [Part 06 — 🖥️✍️ Adding Prompts ➡️](#part-6)


> 📒 **What you'll learn:** How to test static and template resources in the MCP Inspector — and how the Inspector separates them into two distinct sections.

---


### Run it

```bash
mcp dev MCP_Server/server_v3.py
```

Open the URL shown in the terminal and connect:

- **Command** — `py` on Windows, `python` or `python3` on macOS/Linux
- **Arguments** — `MCP_Server/server_v3.py`
- Click **Connect**

---


### Navigate to Resources

Once connected, click **Resources** in the top navigation bar. You'll notice two separate sections — **Resources** (for static) and **Resource Templates** (for template resources).

![Resources and Resource Templates sections](assets/part_05/screenshot_resources_options.jpg)

> 💡 This matches the MCP protocol: static resources are exposed via `resources/list`, template resources via `resources/templates/list` — two separate endpoints.

---


### Test 1 — `releases://list` (Static Resource)

In the **Resources** section, click **List Resources**. You should see `list_releases` appear below.

![List Resources button and list_releases result](assets/part_05/screenshot_resources_list_releases_1.jpg)

Click **`list_releases`** to read it.

![list_releases result](assets/part_05/screenshot_resources_list_releases_2.jpg)

- **1)** `list_releases` — click to select and read
- **2)** Result on the right

```json
{
  "contents": [
    {
      "uri": "releases://list",
      "mimeType": "application/json",
      "text": "{\"releases\": [\"release_20260524_103042\"], \"count\": 1}"
    }
  ]
}
```

Notice the response structure: `uri`, `mimeType`, and `text`. The `text` field contains our JSON payload as a string — this is how MCP always wraps resource content.

✅ Static resource working correctly.

---


### Test 2 — `releases://by/{id}` (Template Resource)

Switch to the **Resource Templates** section and click **List Templates**. You should see `get_release_by_id` appear below.

![List Templates button and get_release_by_id result](assets/part_05/screenshot_resources_list_release_by_id_1.jpg)

Click **`get_release_by_id`**, fill in the `id` parameter with a value from the list above, and click **Read Resource**.

![get_release_by_id with id filled in](assets/part_05/screenshot_resources_list_release_by_id_2.jpg)

- **1)** `get_release_by_id` — click to select
- **2)** `id` field — paste the id from the previous result: `release_20260524_103042`
- **3)** **Read Resource** — click to execute

Result:

![get_release_by_id result](assets/part_05/screenshot_resources_list_release_by_id_3.jpg)

```json
{
  "contents": [
    {
      "uri": "releases://by/release_20260524_103042",
      "mimeType": "text/plain",
      "text": "## What's Changed? \n- Fix login bug\n- Add dark mode\n- Improve performance"
    }
  ]
}
```

Two things to observe here:

- The **URI** is now `releases://by/release_20260524_103042` — the `{id}` placeholder was resolved with the value we passed in.
- The **`mimeType`** is `text/plain` and the **`text`** is genuinely plain text — just the release notes body, no JSON wrapper. Compare this with Test 1 where `mimeType` was `application/json` and `text` contained a JSON string.

✅ Template resource working correctly.

---


### What to keep in mind

> ⚠️ **MCP Inspector caching behaviour:** After calling a template resource (`releases://by/{id}`),
> the Inspector may return cached results for subsequent static resource calls (`releases://list`).
> Refresh the page to reset if you notice stale results.

> 💡 **The two resources are designed to chain:** use `releases://list` to discover available IDs, then `releases://by/{id}` to fetch the notes for a specific one. In our pipeline however, this flow is handled entirely by the `read_last_release()` tool — the resources exist here for exploration and demonstration purposes only.

❎ When you're done, press `Ctrl + C` in the terminal to stop the server.

---


### 🎮 Quiz

*(coming soon)*

---


> 💡 **MCP Curiosity**
> Template resources are a pattern unique to MCP — most APIs require you to know the full URL upfront. In MCP, a client can discover that `releases://by/{id}` exists, understand its parameter from the description, and construct the URI dynamically at runtime. The model can do the same.

[↑ Back to Table of Contents](#table-of-contents)

<a name="part-6"></a>

---

## Part 06 — 🖥️✍️ Adding Prompts

#### ⚡ Quick Navigation: [⬅️ Part 05 — 🖥️📚🔍 Testing Resources](#part-5) | [Part 07 — 🖥️✍️🔍 Testing Prompts ➡️](#part-7)

> 📒 **What you'll learn:** How to define and register prompts in an MCP server — and why they're more powerful than they first appear.

---


### Theory

In MCP, a **Prompt** is a reusable message template that clients can retrieve and pass to an AI model as the starting point for a task.

Think of it like a **culinary recipe**: the ingredients are the parameters you pass in, and the recipe itself is the structured set of instructions that tells the AI exactly how to proceed — what role to adopt, what to produce, and how to format the result. Without the recipe, you might still end up with something edible. With it, you get a consistent, professional dish every time.

This is where the real value of MCP Prompts lies: **not just in the text itself, but in the instructions baked into it**. A well-crafted prompt template shapes the model's behaviour — defining its persona, framing the task, and guiding the output format — so every client that uses it gets the same quality result, without having to reinvent the prompt from scratch.

In practice, this means:

- Prompts live on the **server**, not scattered across client code
- Any client that connects can **discover and reuse** them via `prompts/list`
- Changing the prompt in one place **propagates everywhere** — no need to update each client

---


### Code walkthrough

> 📄 **File:** `MCP_Server/server_v4.py`

Prompts are registered with `@mcp.prompt()` — the same pattern as `@mcp.tool()` and `@mcp.resource()`.

```python
# ─────────────────────────────────────────────
# ✍️ PROMPT — template for generating release notes 
# ─────────────────────────────────────────────
@mcp.prompt()
def generate_release_notes(version: str, changes: str) -> str:
    """Prompt template to generate professional release notes."""
    return (f"""
You are a technical writer. Generate professional release notes for version {version}.

<Raw changes>
{changes}
</Raw changes>

Write clear, concise release notes suitable for a developer audience.
    """)
```

**`@mcp.prompt()`** — registers the function with the MCP server, making it discoverable via `prompts/list`.

**`version` and `changes`** — parameters injected into the template at call time. The client supplies these values when requesting the prompt.

**The docstring** — exposed to clients as the prompt description, just like with tools.

**The return value** — a fully formed string ready to be sent to the model. Notice it's not just a placeholder: it sets a **persona** (`You are a technical writer`), provides **context** (the raw changes), and defines the **expected output** (clear, concise, developer-focused). That's the recipe in action.

---


### 🎮 Quiz

*(coming soon)*

---


> 💡 **MCP Curiosity**  
> Prompts in MCP can include much more than plain strings — including images and embedded resources, allowing models to receive richer multimodal context directly inside the prompt.

[↑ Back to Table of Contents](#table-of-contents)

<a name="part-7"></a>

---

## Part 07 — 🖥️✍️🔍 Testing Prompts

#### ⚡ Quick Navigation: [⬅️ Part 06 — 🖥️✍️ Adding Prompts](#part-6) | [Part 08 — 🔌 MCP Client Setup ➡️](#part-8)

> 📒 **What you'll learn:** How to test prompts in the MCP Inspector — and why what you see here is just the raw template, not the finished dish.

---


### Run it

```bash
mcp dev MCP_Server/server_v4.py
```

Open the URL shown in the terminal and connect:

- **Command** — `py` on Windows, `python` or `python3` on macOS/Linux
- **Arguments** — `MCP_Server/server_v4.py`
- Click **Connect**

---


### Navigate to Prompts

Once connected, click **Prompts** in the top navigation bar, then click **List Prompts** to fetch the prompts registered on your server.

![Prompts navigation](assets/part_07/screenshot_prompts_1.jpg)

1) **Prompts** — click to open the prompts section
2) **List Prompts** — click to fetch registered prompts

---


### Select the prompt

After clicking **List Prompts**, `generate_release_notes` will appear. Click it to open the prompt form on the right.

![generate_release_notes selected](assets/part_07/screenshot_prompts_2.jpg)

1) **List Prompts** — already clicked
2) **`generate_release_notes`** — click to select it; the parameter form appears on the right

---


### Fill in the parameters and run

Fill in the two parameters with any test values, then click **Get Prompt**.

![Prompt parameters and result](assets/part_07/screenshot_prompts_3.jpg)

1) **`version`** — e.g. `567`
2) **`changes`** — e.g. `Visual layout changed. Bug fixed on saving descriptions.`
3) **Get Prompt** — click to execute

The result on the right shows the resolved prompt as a MCP message object:

```json
{
  "description": "Prompt template to generate professional release notes.",
  "messages": [
    {
      "role": "user",
      "content": {
        "type": "text",
        "text": "\nYou are a technical writer. Generate professional release notes for version 567.\n\n<Raw changes>\nVis..."
      }
    }
  ]
}
```

✅ Prompt retrieved and parameters correctly injected.

---


### What you're actually seeing here

Not very exciting, right? And that's expected.

What the Inspector shows is just the **raw template with the parameters injected** — the recipe card, not the cooked meal. The model hasn't seen it yet. No release notes have been generated.

The real value kicks in when a client:
1. Calls `prompts/get` to retrieve this template
2. Passes it as the user message to the Claude API
3. Gets back a polished, professional release notes document

That's the pipeline we're building. The Inspector is just confirming the ingredient list is correct before we start cooking.

---


### What to keep in mind

> ⚠️ The MCP Inspector shows the prompt **before** it reaches a model — it's a static preview, not an AI completion. To see the output, you'd need to pass this message to the Claude API directly.

❎ When you're done, press `Ctrl + C` in the terminal to stop the server.

---


### 🎮 Quiz

*(coming soon)*

---


> 💡 **MCP Curiosity**
> Because prompts are server-side, they can be versioned, A/B tested, and updated without touching client code. In a multi-agent system, this means all agents automatically pick up prompt improvements the next time they call `prompts/get` — no redeploys needed on the client side.

---



### 🖥️ Server complete — what we built

Parts 01–07 covered the full MCP server. Before moving to the client, here's a quick recap of the three primitives and who actually calls them:

| Primitive | Decorator | Who calls it | Purpose |
|---|---|---|---|
| **Tool** | `@mcp.tool()` | The model — autonomously | Actions with side effects |
| **Resource** | `@mcp.resource()` | The MCP client / human | Read-only data access |
| **Prompt** | `@mcp.prompt()` | The MCP client / human | Reusable message templates |

> 💡 **Tools and error handling:** Because tools are called autonomously by the model, the errors they return are part of the model's context — it reads them. A descriptive error like `"Invalid version format: '1.2' does not match expected pattern 'v1.2.0'"` gives the model enough information to self-correct and retry `create_pdf` with the right value. Vague errors produce vague behaviour. The model reads your exceptions and can act accordingly!!! 🤯🤯🤯
>
> Resources and prompts don't share this property — their errors are returned to the client, not the model.


The server is a **capability provider** — it doesn't decide when or how its primitives are used. That intelligence lives on the other side.

Which brings us to Part 08. 👇

[↑ Back to Table of Contents](#table-of-contents)

<a name="part-8"></a>

---

# 🔌MCP Client
## Part 08 — 🔌 MCP Client Setup

#### ⚡ Quick Navigation: [⬅️ Part 07 — 🖥️✍️🔍 Testing Prompts](#part-7) | [Part 09 — 🔌🔧🔍 Testing Tools ➡️](#part-9)

> 📒 **What you'll learn:** How to set up an MCP client from scratch — and how it connects to the server we built in Parts 01–07.

---


### Theory

So far, the server has been running in isolation — we tested it manually via the MCP Inspector.

Now we build the **client**: the component that connects to the server, discovers its capabilities, and exposes them to the AI model.

> 💡 **Recap from Part 01:** The server is a *capability provider* — it doesn't decide when or how its tools are used. The intelligence lives on the client side. The client is what bridges the server and the model.

---


### Wait — how does the server actually receive connections?

Before wiring up the client, there's a detail worth revisiting. Back in Part 01, we ended the server with:

> 📄 **File:** `MCP_Server/server_v1.py`

```python
if __name__ == "__main__":
    mcp.run()
```

This looked simple — but `mcp.run()` actually accepts a `transport` parameter:

```python
mcp.run(transport="stdio")  # this is the default
```

The full signature is:

```python
def run(
    transport: Literal['stdio', 'sse', 'streamable-http'] = "stdio",
    mount_path: str | None = None
) -> None
```

We didn't need to pass it explicitly because `"stdio"` is the default. But now that we're building the client, this matters: **our client needs to communicate over the same transport the server is listening on.**

Since the server uses `stdio` by default, the client will connect via stdio too — launching the server as a subprocess and communicating through its standard input/output streams.

> 💡 **Transport is just a detail — but it must match.** Client and server need to agree on the communication channel. In this project, both use `stdio`.

> ⚠️ **HTTP + SSE and StreamableHTTP** — The MCP ecosystem is evolving fast. You may encounter tutorials referencing `sse` as a transport option. As of MCP spec 2025-03-26, HTTP + SSE has been deprecated and replaced by `streamable-http`. If you're building a remote server, use `streamable-http` instead.

---


### Install dependencies

If you're working in the **same virtual environment** as the server, you already have `mcp` installed — no action needed.

If the client runs in a **separate virtual environment**, install it:

```bash
pip install mcp
```

> ⚠️ The `mcp` package covers both sides — server and client primitives live in the same library. The `[cli]` extra we installed in Part 01 is only needed for the MCP Inspector (dev tooling). For the client, the base package is enough.

---


### Code walkthrough

> 📄 **File:** `MCP_Client/client_v1.py`

#### Imports

```python
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
```

`AsyncExitStack` — manages multiple async resources and guarantees cleanup when the program ends, even if an error occurs. We'll come back to this below.

`ClientSession` — the high-level object that exposes `list_tools()`, `call_tool()`, `read_resource()`, `get_prompt()`, etc. This is what we'll use to talk to the server.

`StdioServerParameters` — defines how to launch the server subprocess (which command, which script).

`stdio_client` — opens the physical stdio communication channel with the server.

---


#### Configuration

```python
SERVER_SCRIPT = "MCP_Server/server_v4.py"
```

The path to the server file. The client will launch it as a subprocess.

---


#### connect_to_mcp_server

This is the core function — it connects to the server and returns a `session` object ready to use.

```python
async def connect_to_mcp_server(exit_stack: AsyncExitStack) -> ClientSession:
    # Defines how to launch the MCP server as a subprocess (command + script path)
    mcp_server_params = StdioServerParameters(
        command="python",
        args=[SERVER_SCRIPT],
    )
    # Spawns the server subprocess and opens the stdio communication channel.
    # exit_stack registers it for automatic cleanup when the program ends.
    # What stdio_client returns: a tuple of two raw streams (read, write)
    stdio_transport = await exit_stack.enter_async_context(
        stdio_client(mcp_server_params)
    )
    read_stream, write_stream = stdio_transport

    # Wraps the raw streams into a high-level ClientSession object.
    # exit_stack registers it too — same pattern, different return value.
    # What ClientSession returns: the session itself — the object you actually use.
    # session exposes: list_tools(), call_tool(), read_resource(), get_prompt(), etc.
    session = await exit_stack.enter_async_context(
        ClientSession(read_stream, write_stream)
    )
    # Performs the MCP handshake — client and server exchange their capabilities
    await session.initialize()

    print("✅ Connected to MCP server\n")
    return session
```

Let's break it down step by step.

---


**Step 1 — StdioServerParameters**

```python
SERVER_SCRIPT = "MCP_Server/server_v4.py"

# (...)

mcp_server_params = StdioServerParameters(
    command="python",
    args=[SERVER_SCRIPT],
)
```

This is the recipe for launching the server. It says: *"run `python MCP_Server/server_v4.py` as a subprocess."*

Nothing has started yet — this is just configuration.

---


**Step 2 — stdio_client (the transport layer)**

```python
stdio_transport = await exit_stack.enter_async_context(
    stdio_client(mcp_server_params)
)
read_stream, write_stream = stdio_transport
```

This actually spawns the server subprocess and opens the communication channel.

`stdio_client` returns a tuple of two raw streams:
- `read_stream` — bytes coming *from* the server
- `write_stream` — bytes going *to* the server

Think of this as the **cable** connecting client and server. It's low-level — just bytes in and out.

> ⚠️ **Why `exit_stack.enter_async_context`?**
> This pattern registers the resource so it gets cleaned up automatically when the program ends. `enter_async_context` calls `__aenter__` to open the resource, and stores `__aexit__` to close it later — you don't have to manage that manually.
> 
> It appears twice here because we have **two separate resources** to manage: the transport (the subprocess + streams) and the session (the protocol layer on top). Each needs its own lifecycle.
>
> 🐇 **Want to go deeper on AsyncExitStack?** → [Asynchronous Context Managers — Medium](https://medium.com/@hitorunajp/asynchronous-context-managers-f1c33d38c9e3)

---


**Step 3 — ClientSession (the protocol layer)**

```python
session = await exit_stack.enter_async_context(
    ClientSession(read_stream, write_stream)
)
await session.initialize()
```

`ClientSession` wraps the raw streams and adds the MCP protocol on top — it knows how to speak MCP, not just move bytes.

`session.initialize()` performs the MCP handshake: client and server exchange their capabilities (`tools/list`, `resources/list`, `prompts/list` metadata). After this step, the client knows what the server can do.
> 🔗 **Source:** [MCP Specification — Lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle) | Google Search: "mcp specs lifecycle"


What you get back — `session` — is the object you'll use for everything from here on:

```python
session.list_tools()
session.call_tool(name, args)
session.read_resource(uri)
session.get_prompt(name, arguments)
```

> 💡 **Transport vs Session — the analogy:**
> The transport is the **cable**, the session is the **browser**. The browser needs the cable, but you only ever interact with the browser.

---


#### Entry point

```python
if __name__ == "__main__":
    pass
```

The client is set up but not doing anything yet — the connection logic is in place, and we'll add the actual calls in the next parts.

---


### What we built

A reusable `connect_to_mcp_server` function that:
1. Launches the MCP server as a subprocess
2. Opens a stdio communication channel
3. Wraps it in a `ClientSession` with full MCP protocol support
4. Returns a `session` ready to use

In Part 09, we'll use this session to call tools directly — no AI involved yet, just verifying the connection works end-to-end.

---


### 🎮 Quiz

*(coming soon)*

---


> 💡 **MCP Curiosity**
> The `stdio` transport is not limited to local processes — it's also how Claude Desktop connects to MCP servers configured in its `claude_desktop_config.json`. When you add a server to Claude Desktop, it launches it as a subprocess and communicates via stdio, exactly like we're doing here.
> 
> 🔗 **Source:** [Claude Desktop - Connect to local MCP servers](https://modelcontextprotocol.io/docs/develop/connect-local-servers)

[↑ Back to Table of Contents](#table-of-contents)

<a name="part-9"></a>

---

## Part 09 — 🔌🔧🔍 Testing Tools

#### ⚡ Quick Navigation: [⬅️ Part 08 — 🔌 MCP Client Setup](#part-8) | [Part 10 — 🔌📚🔍 Testing Resources ➡️](#part-10)

> 📒 **What you'll learn:** How to call MCP tools directly from a Python client — no AI involved yet, just verifying the connection and tool calls work end-to-end.

---


### Theory

In Part 08 we built `connect_to_mcp_server` — a function that returns a `session` ready to use. Now we put it to work.

The goal here is simple: **call the two tools we built on the server and confirm they behave as expected.** This is the client equivalent of what we did in Part 03 with the MCP Inspector — except now we're doing it programmatically.

---


### Code walkthrough

> 📄 **File:** `MCP_Client/client_v2.py`

---

<img src="assets/imgs/dot.png" width="40" alt="ALERT">
Before diving into MCP operations logic, there's a wrapper pattern worth understanding — 
it will repeat in Parts 10 to 13.

```python
import asyncio

# (...)

def test_tools():
    async def test_list_tools():
        async with AsyncExitStack() as stack:
            client_session = await connect_to_mcp_server(stack)
            # ... tool calls go here

    asyncio.run(test_list_tools())
```

Three things happening here:

**`async def test_list_tools()`** — the actual logic lives inside an async function
because MCP operations are async (they involve I/O: spawning a subprocess,
reading streams, waiting for responses).

**`async with AsyncExitStack() as stack`** — creates the exit stack and passes it
to `connect_to_mcp_server`. When the `async with` block ends — whether normally
or due to an error — the stack closes all registered resources automatically:
the session, the streams, the server subprocess.

**`asyncio.run(test_list_tools())`** — the outer `test_tools()` is a plain
synchronous function (our entry point). `asyncio.run()` is the bridge that
starts the event loop and runs the async logic inside it.

> 💡 This outer/inner pattern keeps the entry point synchronous (easy to call
> from `if __name__ == "__main__"`) while the actual work stays async.

---

Now let's see the test code, it is structured in three blocks:

---

#### Block 1 — List available tools

```python
list_tools_result = await client_session.list_tools()
tools = list_tools_result.tools

for idx, tool in enumerate(tools, start=1):
    print(f"{idx})  name: {tool.name} | description: {tool.description}")
```

Calls `session.list_tools()` — the client asks the server *"what tools do you expose?"* and gets back the full list with names and descriptions.

This is the same `tools/list` call the MCP Inspector uses under the hood.

---


#### Block 2 — Call `read_last_release`

```python
tool_name = "read_last_release"
read_last_release = await client_session.call_tool(tool_name)
print(read_last_release)
```

Calls the tool by name with no arguments — matches the server definition:

```python
@mcp.tool()
def read_last_release() -> dict:
    """Reads the most recent release payload from release_data/."""
```

---


#### Block 3 — Call `create_pdf`

```python
tool_name = "create_pdf"
tool_args = {
    'version'       : '444',
    'repo_name'     : 'a/repo/name',
    'release_notes' : 'Fix logging \n Fix backend \n Added button in frontend.',
    'published_at'  : '2026/05/28'
}
create_pdf = await client_session.call_tool(tool_name, tool_args)
print(create_pdf)
```

Here we pass arguments — and they map directly to the server-side function signature:

```python
@mcp.tool()
def create_pdf(version: str, repo_name: str, release_notes: str, published_at: str) -> dict:
```

The key names in `tool_args` must match the parameter names in the function. FastMCP handles the mapping automatically.

---


### Run it

```bash
py MCP_Client/client_v2.py
```

Terminal output:

```
🔧  test_tools
✅ Connected to MCP server

Tools
-----------------------------------------------------------------
1)  name: read_last_release | description: Reads the most recent release payload from release_data/.
2)  name: create_pdf | description: Generates a PDF with the release notes.
-----------------------------------------------------------------

read_last_release call
-----------------------------------------------------------------
meta=None content=[TextContent(type='text', text='{"action": "published", ...}')] isError=False
-----------------------------------------------------------------

create_pdf call
-----------------------------------------------------------------
meta=None content=[TextContent(type='text', text='{"success": true, "file": "release_444_20260529_173135.pdf", ...}')] isError=False
-----------------------------------------------------------------
```

✅ Both tools called successfully via the MCP Client.

---


### Result — the generated PDF

The `create_pdf` call produced a real PDF in `MCP_Server/output/`:

![PDF result](assets/part_09/screenshot_pdf.jpg)

```
Release Notes — a/repo/name
Version: 444
Published: 2026/05/28

Fix logging
Fix backend
Added button in frontend.
```

The `release_notes` string we passed in (`'Fix logging \n Fix backend \n Added button in frontend.'`) was split line by line and rendered as individual paragraphs by ReportLab — exactly as the `create_pdf` tool was built to do in Part 02.

---


### What to keep in mind

> ⚠️ At this stage the client is driving the tool calls manually — we decide what to call and with what arguments. In Part 12, the AI model takes over that decision entirely.

---


### 🎮 Quiz

*(coming soon)*

---


> 💡 **MCP Curiosity**
> `call_tool` returns a `CallToolResult` object — not just the raw output. It includes `content` (the tool's response), `isError` (whether the tool raised an exception), and `meta`. The model reads `isError` too — if a tool fails, it can decide to retry or adjust its approach.

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-10"></a>
## Part 10 — 🔌📚🔍 Testing Resources

#### ⚡ Quick Navigation: [⬅️ Part 09 — 🔌🔧🔍 Testing Tools](#part-9) | [Part 11 — 🔌✍️🔍 Testing Prompts ➡️](#part-11)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-11"></a>
## Part 11 — 🔌✍️🔍 Testing Prompts

#### ⚡ Quick Navigation: [⬅️ Part 10 — 🔌📚🔍 Testing Resources](#part-10) | [Part 12 — 🔌🤖 The AI Pipeline ➡️](#part-12)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-12"></a>
## Part 12 — 🔌🤖 The AI Pipeline

#### ⚡ Quick Navigation: [⬅️ Part 11 — 🔌✍️🔍 Testing Prompts](#part-11) | [Part 13 — 🔌🚀 Running the Pipeline ➡️](#part-13)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-13"></a>
## Part 13 — 🔌🚀 Running the Pipeline

#### ⚡ Quick Navigation: [⬅️ Part 12 — 🔌🤖 The AI Pipeline](#part-12) | [Part 14 — ⚡ FastAPI Webhook ➡️](#part-14)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-14"></a>
## Part 14 — ⚡ FastAPI Webhook

#### ⚡ Quick Navigation: [⬅️ Part 13 — 🔌🚀 Running the Pipeline](#part-13) | [Part 15 — 🌐 Cloudflared ➡️](#part-15)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-15"></a>
## Part 15 — 🌐 Cloudflared

#### ⚡ Quick Navigation: [⬅️ Part 14 — ⚡ FastAPI Webhook](#part-14) | [Part 16 — 🐙 GitHub Webhook ➡️](#part-16)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-16"></a>
## Part 16 — 🐙 GitHub Webhook

#### ⚡ Quick Navigation: [⬅️ Part 15 — 🌐 Cloudflared](#part-15) | [Part 17 — 🔗 Full Pipeline ➡️](#part-17)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-17"></a>
## Part 17 — 🔗 Full Pipeline

#### ⚡ Quick Navigation: [⬅️ Part 16 — 🐙 GitHub Webhook](#part-16) | [Part 18 — 🎮 Discord Setup ➡️](#part-18)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-18"></a>
## Part 18 — 🎮 Discord Setup

#### ⚡ Quick Navigation: [⬅️ Part 17 — 🔗 Full Pipeline](#part-17) | [Part 19 — 📤 Sending the PDF ➡️](#part-19)

*(coming soon)*

[↑ Back to Table of Contents](#table-of-contents)

---


<a name="part-19"></a>
## Part 19 — 📤 Sending the PDF

#### ⚡ Quick Navigation: [⬅️ Part 18 — 🎮 Discord Setup](#part-18) | [Next Steps & Resources ➡️](#next-steps--resources)

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