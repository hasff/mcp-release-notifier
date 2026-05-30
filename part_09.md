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

