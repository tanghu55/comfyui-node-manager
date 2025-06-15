import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

CONFIG_PATH = Path(__file__).parent.parent.parent / "data" / "config.json"

# --- 配置管理 ---
async def get_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {"comfyui_path": "", "python_path": "", "pip_mirror": ""}
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

async def save_config(config_data: Dict[str, Any]):
    CONFIG_PATH.parent.mkdir(exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)

# --- 插件和依赖管理 ---
async def scan_plugins(plugins_dir: str) -> List[Dict[str, Any]]:
    if not os.path.isdir(plugins_dir):
        return []
    
    plugin_list = []
    for item in os.listdir(plugins_dir):
        item_path = os.path.join(plugins_dir, item)
        if os.path.isdir(item_path):
            # 检查是否存在 requirements.txt
            reqs_path = os.path.join(item_path, 'requirements.txt')
            plugin_list.append({
                "name": item,
                "has_reqs": os.path.exists(reqs_path)
            })
    return plugin_list

async def get_plugin_requirements(plugins_dir: str, plugin_name: str) -> List[str]:
    reqs_path = os.path.join(plugins_dir, plugin_name, 'requirements.txt')
    if not os.path.exists(reqs_path):
        return []
    
    with open(reqs_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # 过滤空行和注释
        requirements = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
        return requirements

async def get_installed_packages(python_path: str) -> List[Dict[str, str]]:
    if not os.path.exists(python_path):
        raise FileNotFoundError("Python executable not found")

    try:
        # 使用 pip list 获取已安装包
        result = subprocess.run(
            [python_path, '-m', 'pip', 'list', '--format=json'],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        packages = json.loads(result.stdout)
        return packages
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error getting installed packages: {e}")
        return []

async def install_package(python_path: str, package_name: str, mirror_url: str = None) -> Dict[str, Any]:
    if not os.path.exists(python_path):
        return {"status": "error", "log": "Python executable not found"}

    command = [python_path, '-m', 'pip', 'install', package_name]
    if mirror_url:
        command.extend(['--index-url', mirror_url])
        command.extend(['--trusted-host', Path(mirror_url).host]) # 添加信任主机

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return {"status": "success", "log": result.stdout + result.stderr}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "log": e.stdout + e.stderr}