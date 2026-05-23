import json
from pathlib import Path
from datetime import datetime

# FastMCP
from mcp.server.fastmcp import FastMCP

# ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ─────────────────────────────────────────────
# ⚙️ CONFIGURATION
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
MOCK_DATA_DIR = BASE_DIR / "mock_data"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

mcp = FastMCP("release-notifier")

# ─────────────────────────────────────────────
# 🔧 TOOL 1 — read mock data
# ─────────────────────────────────────────────
@mcp.tool()
def read_mock_release() -> dict:
    """Reads the mock GitHub release payload from mock_data/release_payload.json."""
    path = MOCK_DATA_DIR / "release_payload.json"
    if not path.exists():
        return {"error": "mock_data/release_payload.json not found"}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data

# ─────────────────────────────────────────────
# 🔧 TOOL 2 — create PDF
# ─────────────────────────────────────────────
@mcp.tool()
def create_pdf(version: str, repo_name: str, release_notes: str, published_at: str) -> dict:
    """
    Generates a PDF with the release notes.
    Returns the output filename.
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
# 📚 RESOURCE — exposes mock data as readable source
# ─────────────────────────────────────────────
@mcp.resource(
    "releases://latest",
    description="Returns the latest GitHub release payload from mock data"
)
def get_latest_release() -> str:
    path = MOCK_DATA_DIR / "release_payload.json"
    if not path.exists():
        return json.dumps({"error": "mock_data/release_payload.json not found"})
    return path.read_text(encoding="utf-8")


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


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()