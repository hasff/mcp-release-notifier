# Standard library
from contextlib import AsyncExitStack
import asyncio

# MCP
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client



# ─────────────────────────────────────────────
# ⚙️ CONFIGURATION
# ─────────────────────────────────────────────
SERVER_SCRIPT   = "MCP_Server/server_v4.py"



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
            tool_name = "read_last_release call"
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



# ─────────────────────────────────────────────
# 🚀 ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    test_tools()
    
    pass