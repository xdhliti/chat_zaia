#!/usr/bin/env python
import warnings
import uvicorn
import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes import router


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

app = FastAPI(title="Zaia Agents Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app.include_router(router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    return response

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"[HTTP] Listening on port {port}")
    uvicorn.run(app, host="localhost", port=port)