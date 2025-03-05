#!/usr/bin/env python
import os
import logging
import uvicorn
import warnings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.zaia_agents.routers.chat_routes import router as chat_routes
from src.zaia_agents.routers.status_routes import router as status_routes
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def create_app() -> FastAPI:
    app = FastAPI(title="Zaia Chat Service")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("main")

    app.include_router(chat_routes, prefix="/chat", tags=["chat"])
    app.include_router(status_routes, prefix="/status", tags=["status"])

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        return response

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logging.getLogger("main").info(f"[HTTP] Listening on port {port}")
    uvicorn.run("src.zaia_agents.main:app", host="localhost", port=port, reload=True)
