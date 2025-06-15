from fastapi import APIRouter, HTTPException, Body, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import asyncio
from pathlib import Path
import traceback

from app.core import manager
from app.models.schemas import Config, PluginInfo, InstalledPackage, PackageInstallRequest

router = APIRouter()

# --- 原有的 HTTP 端点保持不变 ---
@router.get("/api/config", response_model=Config)
async def read_config():
    return await manager.get_config()
@router.post("/api/config")
async def write_config(config: Config):
    await manager.save_config(config.dict())
    return {"status": "success", "message": "Configuration saved."}
@router.get("/api/plugins", response_model=List[PluginInfo])
async def list_plugins():
    config = await manager.get_config()
    plugins_dir = config.get("comfyui_path")
    if not plugins_dir:
        raise HTTPException(status_code=400, detail="ComfyUI plugin path is not configured.")
    return await manager.scan_plugins(plugins_dir)
@router.get("/api/plugins/{plugin_name}/requirements", response_model=List[str])
async def list_plugin_requirements(plugin_name: str):
    config = await manager.get_config()
    plugins_dir = config.get("comfyui_path")
    if not plugins_dir:
        raise HTTPException(status_code=400, detail="ComfyUI plugin path is not configured.")
    return await manager.get_plugin_requirements(plugins_dir, plugin_name)
@router.get("/api/python/installed_packages", response_model=List[InstalledPackage])
async def list_installed_packages():
    config = await manager.get_config()
    python_path = config.get("python_path")
    if not python_path:
        raise HTTPException(status_code=400, detail="Python interpreter path is not configured.")
    try:
        return await manager.get_installed_packages(python_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- WebSocket 端点 ---
@router.websocket("/ws/install")
async def websocket_install(websocket: WebSocket):
    await websocket.accept()
    
    try:
        data = await websocket.receive_json()
        package_name = data.get("package_name")
        if not package_name:
            await websocket.send_json({"type": "error", "message": "Package name not provided."})
            await websocket.close()
            return
    except WebSocketDisconnect:
        return
    except Exception as e:
        await websocket.send_json({"type": "error", "message": f"Invalid data received: {str(e)}"})
        await websocket.close()
        return

    config = await manager.get_config()
    python_path = config.get("python_path")
    mirror_url = config.get("pip_mirror")

    if not python_path or not Path(python_path).exists():
        await websocket.send_json({"type": "error", "message": "Python interpreter path is invalid or not configured."})
        await websocket.close()
        return

    # --- 核心修改点：简化命令构建 ---
    command = [python_path, '-m', 'pip', 'install', package_name]
    if mirror_url:
        # 只添加 --index-url 参数，移除 --trusted-host
        command.extend(['--index-url', mirror_url])
    # ------------------------------------

    await websocket.send_json({"type": "log", "message": f"Executing command: {' '.join(command)}"})

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        async def read_stream(stream, ws):
            while True:
                line = await stream.readline()
                if line:
                    await ws.send_json({"type": "log", "message": line.decode('utf-8', errors='ignore').strip()})
                else:
                    break
        
        await asyncio.gather(
            read_stream(process.stdout, websocket),
            read_stream(process.stderr, websocket)
        )

        await process.wait()
        if process.returncode == 0:
            await websocket.send_json({"type": "done", "status": "success", "message": "Installation completed successfully."})
        else:
            await websocket.send_json({"type": "done", "status": "error", "message": f"Installation failed with exit code {process.returncode}."})

    except FileNotFoundError:
        await websocket.send_json({"type": "error", "message": f"Command not found: {python_path}. Please check the Python path."})
    except Exception as e:
        error_details = traceback.format_exc()
        await websocket.send_json({
            "type": "error",
            "message": f"An unexpected error occurred: {str(e)}\n\n--- TRACEBACK ---\n{error_details}"
        })
    finally:
        await websocket.close()