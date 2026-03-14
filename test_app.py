"""测试 FastAPI 启动"""
from fastapi import FastAPI

app = FastAPI(title="Test")

@app.get("/")
async def root():
    return {"status": "ok"}
