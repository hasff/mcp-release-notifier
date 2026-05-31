<a name="part-13"></a>

---

## Part 13 — 🔌🚀 Running the Pipeline

#### ⚡ Quick Navigation: [⬅️ Part 12 — 🔌🤖 The AI Pipeline](#part-12) | [Part 14 — ⚡ FastAPI Webhook ➡️](#part-14)

> 📒 **What you'll learn:** How to run the full AI pipeline for the first time — observe the tool use loop in action, inspect the message metadata layer, and understand why tool descriptions are critical for the model.

---

### Theory

Up to Part 12 we wired everything together. Now we fire it up.

This part has three acts:

1. **Run the pipeline** — watch Claude call the tools autonomously and generate the PDF
2. **Enable debug mode** — inspect the raw message objects flowing through the conversation
3. **Break things on purpose** — remove tool descriptions and see what happens

---

### Code walkthrough

> 📄 **File:** `MCP_Client/client_v6.py`

Three changes from `client_v5.py`:

---

#### 1 — Import `DebugList`

```python
from helpers import DebugList
```

`DebugList` is a drop-in replacement for a regular Python list. Every time a message is appended, it pretty-prints its role and content blocks — making the conversation structure visible in the terminal.

> 💡 `DebugList` inherits from `list` and overrides `append`. The rest of the pipeline doesn't change at all.

---

#### 2 — Add the `DEBUG_PRINT_ALL_MESSAGE_DETAILS` flag

```python
async def run_pipeline(release_payload: dict, DEBUG_PRINT_ALL_MESSAGE_DETAILS = False):
    # (...)
    messages = DebugList() if DEBUG_PRINT_ALL_MESSAGE_DETAILS else []
```

When `True`, `messages` becomes a `DebugList`. When `False`, it's a plain list — no overhead.

---

#### 3 — Add `test_full_pipeline`

```python
def test_full_pipeline():
    sample_payload = {
        "action": "published",
        "release": {
            "tag_name": "v1.2.6760",
            "name": "Release v1.2.6760",
            "body": "## What's Changed?\n- Fix login bug\n- Add dark mode\n- Improve performance",
            "published_at": "2025-05-23T10:00:00Z",
            "html_url": "https://github.com/user/repo/releases/tag/v1.2.6760"
        },
        "repository": {
            "name": "mcp-release-notifier",
            "full_name": "user/mcp-release-notifier",
            "html_url": "https://github.com/user/mcp-release-notifier"
        }
    }
    asyncio.run(run_pipeline(sample_payload, False))
```

This simulates what the webhook will trigger in production — a complete release payload in, a polished PDF out. We start with debug **off** to keep the output clean.

---

### Run 1 — Clean output (debug off)

> ⚠️ Before running, open `MCP_Server/output/` — you'll want to see the PDF appear there after the pipeline finishes.

```bash
py MCP_Client/client_v6.py
```

Terminal output:
```bash
✅ Connected to MCP server
🔧 Tools available: ['read_last_release', 'create_pdf']
✍️  Prompt fetched (266 chars)
🤖 Claude is working...
🔧 Claude calls: read_last_release({})
↳  Result: {"action": "published", "release": {"tag_name": "v1.2.6760", ...
🔧 Claude calls: create_pdf({"version": "v1.2.6760", "repo_name": "mcp-release-notifier", "release_notes": "..."})
↳  Result: {"success": true, "file": "release_v1.2.6760_20260531_170614.pdf", ...
📍✅ Claude finished: Perfect! I've successfully completed all three tasks...
✅ Pipeline complete.
```

Claude autonomously called `read_last_release`, wrote professional release notes, then called `create_pdf`. No manual orchestration — Claude decided the sequence.

---

### 🎉 The WOW moment — the generated PDF

Three raw bullet points in:
```bash 
"body": "## What's Changed?\n- Fix login bug\n- Add dark mode\n- Improve performance" 
```
A structured, professional document out:

![PDF output](assets/part_13/screenshot_pdf_p13.jpg)

