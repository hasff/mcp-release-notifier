# Standard library
import asyncio
from contextlib import AsyncExitStack
import json
from pydantic import AnyUrl

# MCP
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Anthropic
import anthropic

# Environment
import os
from dotenv import load_dotenv
load_dotenv()




# ─────────────────────────────────────────────
# ⚙️ CONFIGURATION
# ─────────────────────────────────────────────
SERVER_SCRIPT   = "MCP_Server/server_v4.py"
CLAUDE_MODEL    = "claude-haiku-4-5"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

assert ANTHROPIC_API_KEY, "Error: ANTHROPIC_API_KEY not found. Check your .env file."


# ─────────────────────────────────────────────
# 🔌 CONNECTION — setup & cleanup
# ─────────────────────────────────────────────
async def connect_to_mcp_server(exit_stack: AsyncExitStack) -> ClientSession:
    # Defines how to launch the MCP server as a subprocess (command + script path)
    mcp_server_params = StdioServerParameters(
        command="python",
        args=[SERVER_SCRIPT],
    )
    # Opens the physical communication channel with the server subprocess.
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



# ─────────────────────────────────────────────
# 🤖 PIPELINE — the heart of it
# ─────────────────────────────────────────────
async def run_pipeline(release_payload: dict):

    async with AsyncExitStack() as stack:
        client_session = await connect_to_mcp_server(stack)

        # — List available tools and convert to Anthropic format
        tools_result = await client_session.list_tools()
        anthropic_tools = [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema,
            }
            for t in tools_result.tools
        ]
        print(f"🔧 Tools available: {[t['name'] for t in anthropic_tools]}\n")

        # — Fetch prompt template from MCP server
        #   The client fetches it and injects it into the initial message.
        #   The model is not aware of this step — it just receives the instructions.
        version     = release_payload.get("release", {}).get("tag_name", "unknown")
        raw_changes = release_payload.get("release", {}).get("body", "")
        prompt_result = await client_session.get_prompt(
            "generate_release_notes",
            arguments={"version": version, "changes": raw_changes}
        )
        prompt_text = prompt_result.messages[0].content.text
        print(f"✍️  Prompt fetched ({len(prompt_text)} chars)\n")

        # — Build initial message
        initial_message = f"""
            A new GitHub release has been published. Here is the release payload:

            <payload>
            {json.dumps(release_payload, indent=2)}
            </payload>

            Your task:
            1. Call read_last_release to confirm the release data.
            2. Using the instructions below, write professional release notes for this release.
            3. Call create_pdf with the professional release notes you wrote.

            Instructions for writing the release notes:
            {prompt_text}
        """

        # ── TOOL USE LOOP ─────────────────────────────────────────────────────
        # Claude receives the tools + initial message.
        # It decides autonomously which tools to call and in what order.
        # The client executes each tool call and returns the result to Claude.
        # The loop ends when Claude stops calling tools (stop_reason == "end_turn").
        # ─────────────────────────────────────────────────────────────────────
        anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        messages = [{"role": "user", "content": initial_message}]

        print("🤖 Claude is working...\n")

        while True:
            response = anthropic_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1024,
                tools=anthropic_tools,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                final_text = next(
                    (b.text for b in response.content if hasattr(b, "text")), "Done."
                )
                print(f"✅ Claude finished: {final_text}")
                break

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"   🔧 Claude calls: {block.name}({json.dumps(block.input)})")
                    result = await client_session.call_tool(block.name, block.input)
                    result_text = result.content[0].text
                    print(f"   ↳  Result: {result_text[:120]}...\n")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    })

            messages.append({"role": "user", "content": tool_results})

        print("\n✅ Pipeline complete.")


# ────────────────────────────────────────────────────────────────────────── #
#  🧪 MANUAL TESTS ───────────────────────────────────────────────────────── #
# ─────────────────────────────────────────────────────────────────────────── #

# List tools only (no pipeline)
# Useful to confirm the client connects and the server exposes the right tools.
# -------------------------------------------------------------------------
def test_tools():
    print("🔧  test_tools")
    async def test_list_tools():
        async with AsyncExitStack() as stack:
            client_session = await connect_to_mcp_server(stack)

            list_tools_result = await client_session.list_tools()
            tools = list_tools_result.tools
            print("Tools")
            print("-----------------------------------------------------------------")
            for idx, tool in enumerate(tools, start=1):
                print(f"{idx})  name: {tool.name} | description: {tool.description}")

            print("-----------------------------------------------------------------\n")

            print("read_last_release call")
            print("-----------------------------------------------------------------")
            tool_name = "read_last_release"
            read_last_release = await client_session.call_tool(tool_name)
            print(read_last_release)
            print("-----------------------------------------------------------------\n")

            print("create_pdf call")
            print("-----------------------------------------------------------------")
            tool_name = "create_pdf"
            tool_args = {
                'version'       : '444',
                'repo_name'     : 'a/repo/name',
                'release_notes' : 'Fix logging \n Fix backend \n Added button in frontend.',
                'published_at'  : '2026/05/28'
            }
            create_pdf = await client_session.call_tool(tool_name, tool_args)
            print(create_pdf)
            print("-----------------------------------------------------------------\n")
            
    asyncio.run(test_list_tools())

# Read resource releases://list
# Confirms the static resource is reachable.
# -------------------------------------------------------------------------
def test_resources():
    print("📚  test_resources")
    async def test_read_resource():
        
        async with AsyncExitStack() as stack:
            client_session = await connect_to_mcp_server(stack)

            # 🚨 STATIC RESOURCES
            list_resources_result = await client_session.list_resources()
            print("Static Resources")
            print("-----------------------------------------------------------------")
            for r in list_resources_result.resources:
                # print(f"  - Name: {r.name} | URI: {r.uri} | Description: {r.description}")
                print(r)
            print("-----------------------------------------------------------------\n")

            result = await client_session.read_resource(AnyUrl("releases://list"))
            print("Static Resource result") 
            print("-----------------------------------------------------------------")
            print(result.contents[0].text)
            print("-----------------------------------------------------------------\n\n")



            # 🚨 TEMPLATE RESOURCES  
            list_resource_templates_result = await client_session.list_resource_templates()
            print("Template Resources")
            print("-----------------------------------------------------------------")            
            for r in list_resource_templates_result.resourceTemplates:
                # print(f"  - Name: {r.name} | URI: {r.uriTemplate} | Description: {r.description}")
                print(r)
            print("-----------------------------------------------------------------\n")   

            id = "release_20260524_103042" 
            uri = f"releases://by/{id}"            
            print(f"Template Resource result for uri= {uri}") 
            print("-----------------------------------------------------------------")
            result_dynamic = await client_session.read_resource(AnyUrl(uri))
            print(result_dynamic.contents[0].text)
            print("-----------------------------------------------------------------\n\n")                                 
    asyncio.run(test_read_resource())

# Fetch prompt only
# Confirms the prompt template is rendered correctly with injected parameters.
# -------------------------------------------------------------------------
def test_prompts():
    print("✍️  test_prompts")
    async def test_get_prompt():
        async with AsyncExitStack() as stack:
            client_session = await connect_to_mcp_server(stack)

            list_prompts_result = await client_session.list_prompts()
            prompts_list = list_prompts_result.prompts

            print("Prompts")
            print("-----------------------------------------------------------------")
            for idx, prompt in enumerate(prompts_list, start=1):
                print(f"{idx}) name= {prompt.name} | description= {prompt.description} | arguments: {[x.name for x in prompt.arguments]}")

            print("-----------------------------------------------------------------\n")

            result = await client_session.get_prompt(
                "generate_release_notes",
                arguments={"version": "v1.0.0", "changes": "- Fixed bug\n- Added feature"}
            )
            print("Prompt text")
            print("-----------------------------------------------------------------\n")
            print(result.messages[0].content.text)
            print("-----------------------------------------------------------------\n")
    asyncio.run(test_get_prompt())

# Full pipeline with a sample release payload
# Simulates what the webhook will trigger in production.
# -------------------------------------------------------------------------
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
    asyncio.run(run_pipeline(sample_payload))

# ─────────────────────────────────────────────
# 🚀 ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # test_tools()
    # test_resources()
    # test_prompts()

    # test_full_pipeline()

    pass







