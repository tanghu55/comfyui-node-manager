import uvicorn
import asyncio
import sys

if __name__ == "__main__":
    # 这一部分是关键，它确保在 uvicorn 启动之前，
    # 就在主进程中为 Windows 设置好正确的事件循环策略。
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 以编程方式启动 uvicorn，这样可以完全控制启动环境
    # 我们甚至可以在这里重新启用 reload 功能，因为它在编程模式下通常工作得更好
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)