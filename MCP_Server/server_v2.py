# Standard library
import json
from pathlib import Path
from datetime import datetime

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


if __name__ == "__main__":
    mcp.run()