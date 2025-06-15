from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints
import asyncio
import sys

# --- 核心修改点：在 Windows 上设置事件循环策略 ---
# 检查当前操作系统是否为 Windows
if sys.platform == "win32":
    # 设置事件循环策略为 ProactorEventLoop，以支持 asyncio 的子进程功能
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# ----------------------------------------------------


app = FastAPI(title="ComfyUI Node Manager")

# 配置 CORS 中间件，允许前端（例如，运行在 localhost:5173）访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # 增加 127.0.0.1
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to ComfyUI Node Manager API"}