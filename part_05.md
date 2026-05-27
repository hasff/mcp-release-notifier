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