import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

N8N_WEBHOOK_URL = os.environ["N8N_WEBHOOK_URL"]
N8N_WEBHOOK_TOKEN = os.environ["N8N_WEBHOOK_TOKEN"]


@app.post("/api/triage")
async def triage(request: Request):
    body = await request.json()
    mensaje = body.get("mensaje", "").strip()

    if len(mensaje) < 3 or len(mensaje) > 1000:
        return JSONResponse(
            {"error": "El mensaje debe tener entre 3 y 1000 caracteres"},
            status_code=400,
        )

    async with httpx.AsyncClient(timeout=110) as client:
        try:
            resp = await client.post(
                N8N_WEBHOOK_URL,
                json={"mensaje": mensaje},
                headers={"x-api-key": N8N_WEBHOOK_TOKEN},
            )
            resp.raise_for_status()
            data = resp.json()
            return {"respuesta": data.get("respuesta", "Sin respuesta del agente")}
        except httpx.HTTPStatusError as e:
            return JSONResponse(
                {"error": f"n8n respondió {e.response.status_code}"}, status_code=502
            )
        except Exception:
            return JSONResponse({"error": "Error al conectar con n8n"}, status_code=502)
