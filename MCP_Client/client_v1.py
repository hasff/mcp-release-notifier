# Standard library
from contextlib import AsyncExitStack

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



# ─────────────────────────────────────────────
# 🚀 ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":

    pass