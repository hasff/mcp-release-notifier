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

