# Standard library
import json
from pathlib import Path
from datetime import datetime
import httpx
import os

# MCP
from mcp.server.fastmcp import FastMCP

# ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# ─────────────────────────────────────────────
# ⚙️ CONFIGURATION
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
RELEASE_DATA_DIR = BASE_DIR / "release_data"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

mcp = FastMCP("release-notifier")

# ─────────────────────────────────────────────
# 🔧 TOOL 1 — read last release
# ─────────────────────────────────────────────
@mcp.tool()
def read_last_release() -> dict:
    """Reads the most recent release payload from release_data/."""
    files = sorted(RELEASE_DATA_DIR.glob("release_[0-9]*.json"))
    if not files:
        return {"error": "No release files found in release_data/"}
    return json.loads(files[-1].read_text(encoding="utf-8"))

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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"release_{version}_{timestamp}.pdf"
    output_path = OUTPUT_DIR / filename

    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Release Notes — {repo_name}", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Version: {version}", styles["Heading2"]))
    story.append(Paragraph(f"Published: {published_at}", styles["Normal"]))
    story.append(Spacer(1, 12))

    for line in release_notes.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 6))

    doc.build(story)

    return {"success": True, "file": filename, "path": str(output_path)}

# ─────────────────────────────────────────────
# 🔧 TOOL 3 — send pdf to discord
# ─────────────────────────────────────────────
@mcp.tool()
async def send_release_to_discord(pdf_path: str, repo_name: str, version: str) -> dict:
    """
    Sends the generated PDF release notes to a Discord channel via Webhook.
    
    Args:
        pdf_path: The absolute or relative path to the PDF file.
        repo_name: Name of the repository.
        version: The release version tag.
    """
    path = Path(pdf_path)
    if not path.exists():
        return {"success": False, "error": f"File not found at {pdf_path}"}

    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not discord_webhook_url:
        return {"success": False, "error": "DISCORD_WEBHOOK_URL not configured on server"}

    payload = {"content": f"🚀 **New Release Published!**\nRepository: `{repo_name}`\nVersion: `{version}`"}
    
    async with httpx.AsyncClient() as client:
        with open(path, "rb") as f:
            files = {"file": (path.name, f, "application/pdf")}
            response = await client.post(discord_webhook_url, data=payload, files=files)

    if response.status_code in [200, 204]:
        return {"success": True, "message": "PDF successfully sent to Discord"}
    return {"success": False, "status_code": response.status_code, "error": response.text}


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

# ─────────────────────────────────────────────
# 📚 RESOURCE 2 — template resource
# Returns a specific release notes by id (e.g. releases://release_20250524_143000).
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



if __name__ == "__main__":
    mcp.run()