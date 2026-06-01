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

#### 3 — Print `stop_reason` on every loop iteration

```python
while True:
    response = anthropic_client.messages.create(...)

    print(f"""    
___________________________________________
|
| 🛑 STOP REASON ==> {response.stop_reason}  
|__________________________________________\n""")

    messages.append({"role": "assistant", "content": response.content})
```

`stop_reason` is printed immediately after each API response, before anything else. This makes the loop's decision point visible in the terminal — you can see in real time whether Claude is requesting another tool call or wrapping up.

Two possible values in this pipeline:

| `stop_reason` | Meaning | Loop behaviour |
|---|---|---|
| `tool_use` | Claude wants to call a tool | Continue — execute tools, return results |
| `end_turn` | Claude is done | Break — extract final text, exit loop |

---

#### 4 — Add `test_full_pipeline`

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

```python
if __name__ == "__main__":
    # test_tools()
    # test_resources()
    # test_prompts()
    test_full_pipeline()
    pass
```

> ⚠️ Before running, open `MCP_Server/output/` in your file explorer — you'll want to see the PDF appear there after the pipeline finishes.

---

### Run 1 — Clean output (debug off)

```bash
py MCP_Client/client_v6.py
```

Terminal output:

```
✅ Connected to MCP server

🔧 Tools available: ['read_last_release', 'create_pdf']

✍️  Prompt fetched (266 chars)

🤖 Claude is working...

___________________________________________
|
| 🛑 STOP REASON ==> tool_use  
|__________________________________________

   🔧 Claude calls: read_last_release({})
   ↳  Result: {"action": "published", "release": {"tag_name": "v1.2.6760", ...

___________________________________________
|
| 🛑 STOP REASON ==> tool_use  
|__________________________________________

   🔧 Claude calls: create_pdf({"version": "v1.2.6760", "repo_name": "mcp-release-notifier", "release_notes": "..."})
   ↳  Result: {"success": true, "file": "release_v1.2.6760_20260531_170614.pdf", ...

___________________________________________
|
| 🛑 STOP REASON ==> end_turn  
|__________________________________________

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

> Remember this?
>
> 📄 **File:** `MCP_Server/server_v4.py`
```python
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

That's the prompt template doing its job — turning `"Fix login bug"` into a full paragraph. ✅

---

### Run 2 — Debug mode (metadata layer visible)

Now let's look under the hood. Change the flag in `test_full_pipeline`:

```python
asyncio.run(run_pipeline(sample_payload, True))
```

Run again:

```bash
py MCP_Client/client_v6.py
```

The terminal now shows every message object as it flows through the conversation. Here's what each one means:

---

#### Message 1 — User (initial)

😎 **---->** 💻
```
[METADATA LAYER] ─── Message Object ────────────────────────────────────
 ├── Role: USER 😎
 └── Content Blocks (Total: 1):
      ├── [Block Type]: Raw String Fallback
      └── [Payload]: A new GitHub release has been published...
```

The initial user message — release payload plus writing instructions. A single string block.

---

#### Message 2 — Assistant (first tool call)

😎 **<----** 💻
```
___________________________________________
|
| 🛑 STOP REASON ==> tool_use  
|__________________________________________

[METADATA LAYER] ─── Message Object ────────────────────────────────────
 ├── Role: ASSISTANT 💻
 └── Content Blocks (Total: 2):
      ├── [Block #0 Type]: TEXT
      │  └── [Preview]: "I'll help you process this GitHub release..."
      └── [Block #1 Type]: TOOL_USE
         ├── Tool Name: read_last_release
         ├── Execution ID: toolu_01JeLC5B3EuAJqF9Gbcgcis6
         └── Arguments Schema (JSON Input): {}
```

Claude responds with **two blocks**: a reasoning text block and a `tool_use` block. `stop_reason == "tool_use"` — the loop continues.
>🚨 Did you noticed that `Execution ID: toolu_01JeLC5B3EuAJqF9Gbcgcis6`? 🚨

---

#### Message 3 — User (tool result)

😎 **---->** 💻
```
[METADATA LAYER] ─── Message Object ────────────────────────────────────
 ├── Role: USER 😎
 └── Content Blocks (Total: 1):
      └── [Block #0 Type]: TOOL_RESULT
         ├── Responding To ID: toolu_01JeLC5B3EuAJqF9Gbcgcis6
         └── Execution Output: {"action": "published", ...}
```

The client executes the tool and returns the result. **Responding To ID** matches the 🚨 `Execution ID` 🚨 from Message 2 — this is how Claude correlates results to requests.

![Example: Why tool_use_id is important?](assets/part_13/screenshot_remember_p13.jpg)

---

#### Message 4 — Assistant (second tool call)

😎 **<----** 💻
```
___________________________________________
|
| 🛑 STOP REASON ==> tool_use  
|__________________________________________

[METADATA LAYER] ─── Message Object ────────────────────────────────────
 ├── Role: ASSISTANT 💻
 └── Content Blocks (Total: 2):
      ├── [Block #0 Type]: TEXT
      │  └── [Preview]: "Great! The release data has been confirmed. Now I'll create..."
      └── [Block #1 Type]: TOOL_USE
         ├── Tool Name: create_pdf
         ├── Execution ID: toolu_01N2srZnKD4oiiHVNHNbrPQ4
         └── Arguments Schema (JSON Input):
             {
               "version": "v1.2.6760",
               "repo_name": "mcp-release-notifier",
               "release_notes": "# Release Notes - v1.2.6760\n\n..."
             }
```

Claude "asks" MCP Client to call `create_pdf` with the **fully written release notes** already embedded in the arguments. The model wrote them — not us.

---

#### Message 5 — User (tool result)

😎 **---->** 💻
```
[METADATA LAYER] ─── Message Object ────────────────────────────────────
 ├── Role: USER 😎
 └── Content Blocks (Total: 1):
      └── [Block #0 Type]: TOOL_RESULT
         ├── Responding To ID: toolu_01N2srZnKD4oiiHVNHNbrPQ4
         └── Execution Output: {"success": true, "file": "release_v1.2.6760_20260531_171604.pdf", ...}
```

PDF created. Result returned to Claude.

---

#### Message 6 — Assistant (end_turn)

😎 **<----** 💻
```
___________________________________________
|
| 🛑 STOP REASON ==> end_turn  
|__________________________________________

[METADATA LAYER] ─── Message Object ────────────────────────────────────
 ├── Role: ASSISTANT 💻
 └── Content Blocks (Total: 1):
      └── [Block #0 Type]: TEXT
         └── [Preview]: "Perfect! I've successfully completed all three tasks..."
```

`stop_reason == "end_turn"`. No more tool calls. The loop exits.

---

### What the debug layer reveals

Six messages total. Every single one was included in the last API call. That's the stateless reality of LLM APIs: **the client maintains the full conversation history and sends it in its entirety on every request.**

Each iteration of the loop adds two messages — one assistant response and one user message with the tool results — and the next call carries everything accumulated so far. Claude can only "remember" what we explicitly send back to it. And this is not optional — imagine a tool that depends on the output of a previous one: if the `read_last_release` result isn't in the history, Claude has no way to pass the correct version or repo name to `create_pdf`. Drop a `tool_result` from the list and the chain breaks.

Look at this line in the pipeline:

```python
response = anthropic_client.messages.create(
    model=CLAUDE_MODEL,
    max_tokens=1024,
    tools=anthropic_tools,
    messages=messages,   # 👈 THE ENTIRE HISTORY, EVERY TIME
)
```

`messages` is not "the latest message". It's the full list — growing with every iteration:

```
Iteration 1  →  messages = [msg_1]
Iteration 2  →  messages = [msg_1, msg_2, msg_3]
Iteration 3  →  messages = [msg_1, msg_2, msg_3, msg_4, msg_5]
```

By the time Claude produces its final `end_turn` response, the API call carries all 6 messages. Claude reads the entire conversation from scratch on every call — there is no server-side session, no hidden state, no memory outside of what you send. This is also why long conversations with any LLM — ChatGPT, Claude, Gemini — feel slower and less reliable over time: every reply re-processes the entire history, and as the context grows, so does latency, cost, and the probability of the model losing the thread.

> 💡 **The conversation history is the memory.** Strip any message from the list and Claude loses that context permanently. The `messages` list *is* the mind of the agent.

---

### 🎮 Quiz

*(coming soon)*

---

> 💡 **MCP Curiosity**
> The `tool_use_id` / `tool_result` pairing is part of the Anthropic Messages API spec, not MCP. MCP returns the execution result; the client wraps it in the correct API format. This separation — MCP handles tool execution, the Anthropic SDK handles conversation structure — is what makes the architecture composable.

[↑ Back to Table of Contents](#table-of-contents_)
