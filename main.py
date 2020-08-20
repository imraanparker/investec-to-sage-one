# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from integrations.api import sageone

app = FastAPI(
    docs_url="/api",
    redoc_url=None,
    title="Investec to Accounting Systems",
    description="Import transactions from Investec to different Accounting Systems",
    version="1.0.0")

@app.get("/", tags=["main"])
def status() -> str:
    """Status check"""
    return PlainTextResponse("OK")

app.include_router(
    sageone.router,
    prefix="/sageone",
    tags=["sageone"]
)