from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.dependencies import init_dialogue_engine
from app.api.routers import chat_router
from app.infrastructure.database import init_engine, close_engine
from app.infrastructure.http_client import init_http_client, close_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_engine()
    init_http_client()
    init_dialogue_engine()
    yield  # FASTAPI 处理请求....
    await close_engine()  # 应用关闭的时候才执行到
    await  close_http_client()


# 创建fastapi对象，注册路由
app = FastAPI(description="OpsPilot AI 出海用户支持与运营协同 Agent",lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:18082", "http://localhost:18082"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# app = FastAPI(description="智能客服系统")
app.include_router(chat_router)

frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
