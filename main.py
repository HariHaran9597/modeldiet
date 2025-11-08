from fastapi import FastAPI, HTTPException, Request
import httpx
import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI(title="Gemini Proxy API with Token Counting")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

@app.post("/v1/gemini/generate")
async def generate(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt")
        if not prompt:
            raise HTTPException(status_code=400, detail="Missing 'prompt'")

        # 1️⃣ Token counting
        token_info = gemini_model.count_tokens(prompt)
        token_count = token_info.total_tokens

        # 2️⃣ Send the prompt to Gemini (same working logic as before)
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GEMINI_URL, json=payload)
            response.raise_for_status()
            result = response.json()

        # 3️⃣ Return both model response and token count
        return {
            "status": "success",
            "tokens_used": token_count,
            "response": result
        }

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Gemini API timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Gemini API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
