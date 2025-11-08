from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import httpx, time
import google.generativeai as genai
from database import SessionLocal, RequestLog
from config import GEMINI_API_KEY

# --------------------------------------------------------------------
# FastAPI + Gemini configuration
# --------------------------------------------------------------------
app = FastAPI(title="Gemini Proxy with SQLite Logging")

# Configure Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# Gemini endpoint
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# --------------------------------------------------------------------
# POST /v1/gemini/generate
# Logs every request into SQLite
# --------------------------------------------------------------------
@app.post("/v1/gemini/generate")
async def generate(request: Request):
    session = SessionLocal()
    start_time = time.time()

    try:
        data = await request.json()
        prompt = data.get("prompt")
        if not prompt:
            return {"error": "Missing 'prompt'"}

        # Count tokens using Gemini SDK
        token_info = gemini_model.count_tokens(prompt)
        tokens = token_info.total_tokens

        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GEMINI_URL, json=payload)
            latency_ms = (time.time() - start_time) * 1000
            rate_limited = (response.status_code == 429)

        # Log request in SQLite
        log_entry = RequestLog(
            prompt=prompt[:200],
            tokens=tokens,
            latency_ms=latency_ms,
            rate_limited=rate_limited,
        )
        session.add(log_entry)
        session.commit()

        return {
            "status": "logged",
            "tokens": tokens,
            "latency_ms": latency_ms,
            "rate_limited": rate_limited,
            "response_status": response.status_code,
        }

    except Exception as e:
        session.rollback()
        return {"error": str(e)}
    finally:
        session.close()


# --------------------------------------------------------------------
# GET /logs
# Fetch latest 100 logs for quick inspection
# --------------------------------------------------------------------
@app.get("/logs")
def get_logs():
    session = SessionLocal()
    logs = session.query(RequestLog).order_by(RequestLog.id.desc()).limit(100).all()
    session.close()
    return [
        {
            "id": l.id,
            "prompt": l.prompt,
            "tokens": l.tokens,
            "latency_ms": l.latency_ms,
            "rate_limited": l.rate_limited,
            "timestamp": l.timestamp,
        }
        for l in logs
    ]


# --------------------------------------------------------------------
# GET /export_db
# Download the SQLite DB file for analysis
# --------------------------------------------------------------------
@app.get("/export_db")
def export_db():
    return FileResponse("./modeldiet.db", media_type="application/octet-stream")
