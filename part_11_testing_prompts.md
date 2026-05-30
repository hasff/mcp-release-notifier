> 📒 **What you'll learn:** How to list and retrieve prompts from a Python client — and what the rendered template actually looks like before it reaches a model.

---


### Theory

In Part 07 we tested prompts manually via the MCP Inspector. Now we do the same programmatically.

The flow is straightforward:
1. **Discover** — ask the server what prompts are available (`list_prompts`)
2. **Retrieve** — fetch a specific prompt with injected parameters (`get_prompt`)

Remember, no model is involved yet — this is just confirming the template is reachable and renders correctly.

---


### Code walkthrough

> 📄 **File:** `MCP_Client/client_v4.py`

The test is wrapped in the same outer/inner async pattern used in Parts 09 and 10 — `test_prompts()` as the sync entry point, `test_get_prompt()` as the async logic inside.

---

#### Block 1 — List available prompts

```python
list_prompts_result = await client_session.list_prompts()
prompts_list = list_prompts_result.prompts

for idx, prompt in enumerate(prompts_list, start=1):
    print(f"{idx}) name= {prompt.name} | description= {prompt.description} | arguments: {[x.name for x in prompt.arguments]}")
```

**`client_session.list_prompts()`** — asks the server *"what prompts do you expose?"*. Same discovery pattern as `list_tools()` and `list_resources()`.

**`.prompts`** — the list of prompt metadata objects. Each one exposes `name`, `description`, and `arguments` — a list of parameter objects, each with a `.name` attribute.

**`[x.name for x in prompt.arguments]`** — extracts just the parameter names into a clean list. This tells us exactly what arguments `get_prompt` will need.

---


#### Block 2 — Retrieve a specific prompt

```python
result = await client_session.get_prompt(
    "generate_release_notes",
    arguments={"version": "v1.0.0", "changes": "- Fixed bug\n- Added feature"}
)
print(result.messages[0].content.text)
```

**`client_session.get_prompt(name, arguments)`** — fetches the prompt template with the parameters injected. The `arguments` dict keys must match the parameter names discovered in Block 1.

**`result.messages[0].content.text`** — the rendered prompt string, ready to be passed to the Claude API as a user message. The `messages` structure mirrors what the API expects.

---


### Run it

```python
if __name__ == "__main__":
    # test_tools()
    # test_resources()
    test_prompts()
```

```bash
py MCP_Client/client_v4.py
```

Terminal output:

```
✍️  test_prompts
✅ Connected to MCP server

Prompts
-----------------------------------------------------------------
1) name= generate_release_notes | description= Prompt template to generate professional release notes. | arguments: ['version', 'changes']
-----------------------------------------------------------------

Prompt text
-----------------------------------------------------------------

You are a technical writer. Generate professional release notes for version v1.0.0.

<Raw changes>
- Fixed bug
- Added feature
</Raw changes>

Write clear, concise release notes suitable for a developer audience.
    
-----------------------------------------------------------------
```

✅ Prompt listed and retrieved successfully via the Python client.

---


### Quick reference — Prompts vs Tools vs Resources

| | Tools | Resources | Prompts |
|---|---|---|---|
| **List method** | `list_tools()` | `list_resources()` / `list_resource_templates()` | `list_prompts()` |
| **Access via** | `.tools` | `.resources` / `.resourceTemplates` | `.prompts` |
| **Fetch method** | `call_tool(name, args)` | `read_resource(AnyUrl(...))` | `get_prompt(name, arguments)` |
| **Returns** | `CallToolResult` | `ReadResourceResult` | `GetPromptResult` |

---


### What to keep in mind

> ⚠️ `get_prompt` returns the **rendered template** — not a model completion. The parameters are injected, the string is built, but the model hasn't seen it yet. To generate actual release notes, you'd pass `result.messages` directly to the Claude API.

> 💡 **`result.messages` is already API-shaped.** The structure returned by `get_prompt` matches what the Claude API expects in `messages`.

---


### 🎮 Quiz

*(coming soon)*

---


> 💡 **MCP Curiosity**
> `list_prompts()`, `list_tools()`, and `list_resources()` all follow the same discovery pattern — the MCP protocol was designed so that a model can introspect any server's full capabilities at runtime, without prior knowledge. This is what makes MCP composable: connect to a new server, discover what it offers, and start using it — no hardcoding needed.