# Standard library
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel
from typing import Any

# FastAPI
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Header

# Pipeline
# 1. Allow Python to see other folders in the project
sys.path.append(str(Path(__file__).parent.parent))

RELEASE_DATA_DIR = Path(__file__).parent.parent / "MCP_Server" / "release_data"
RELEASE_DATA_DIR.mkdir(exist_ok=True)

# 2. Now we can safely import from MCP_Client
sys.path.append(str(Path(__file__).parent.parent / "MCP_Client")) 
from MCP_Client.client_v8 import run_pipeline 

# FOR TEST PURPOSES
PIPELINE_IS_ACTIVE = True

# GITHUT SECRET
import hashlib
import hmac
import os
WEBHOOK_SECRET = os.environ["GITHUB_WEBHOOK_SECRET"]

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    if not signature_header:
        return False
    
    expected_signature = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)

# ─────────────────────────────────────────────
# ⚙️ CONFIGURATION
# ─────────────────────────────────────────────
app = FastAPI(title="mcp-release-notifier webhook")


# ─────────────────────────────────────────────
# ❤️ HEALTH CHECK
# ─────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


# ─────────────────────────────────────────────
# ⚡ WEBHOOK — receives GitHub events
# ─────────────────────────────────────────────
@app.post("/webhook")
async def github_webhook(request: Request):

    # ── 0. Verify Signature ────────────────────────
    body = await request.body()

    signature = request.headers.get("X-Hub-Signature-256")

    if not verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")


    # ── 1. Parse body ────────────────────────
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # ── 2. Filter — only care about releases ─
    event_type = request.headers.get("X-GitHub-Event", "")
    if event_type != "release":
        return JSONResponse({"ignored": True, "reason": f"event '{event_type}' is not a release"})

    # ── 3. Filter — only 'published' action ──
    action = payload.get("action", "")
    if action != "published":
        return JSONResponse({"ignored": True, "reason": f"action '{action}' is not 'published'"})

    if PIPELINE_IS_ACTIVE:
        # ── 4 Save payload to release_data ─────
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"release_{timestamp}.json"
        (RELEASE_DATA_DIR / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"💾 Saved payload to release_data/{filename}")

        # ── 5. Fire the pipeline ─────────────────
        print(f"🚀 Release received: {payload['release']['tag_name']} — triggering pipeline...")
        asyncio.create_task(run_pipeline(payload))

    return JSONResponse({"received": True, "tag": payload["release"]["tag_name"]})


# ─────────────────────────────────────────────
# 🚀 ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("webhook_v4:app", host="0.0.0.0", port=8000, reload=True)
