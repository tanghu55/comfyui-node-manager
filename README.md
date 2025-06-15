ComfyUI 依赖管理工具 (ComfyUI Node Manager) - 开发者使用说明
欢迎使用 ComfyUI 依赖管理工具！
本文档为需要从源代码运行本项目的开发者或高级用户提供指引。如果您是普通用户，请寻找已打包的 .exe 版本和对应的使用说明。
本项目采用前后端分离架构：
后端: FastAPI (Python)
前端: Vue.js (JavaScript)
系统要求
Python (版本 3.8 或更高)
Node.js (版本 16.x 或更高)，并附带 npm 包管理器
🛠️ 环境设置与安装
您需要分别为后端和前端设置环境并安装依赖。
1. 克隆项目
首先，从代码仓库克隆本项目到您的本地计算机。
git clone <your-repository-url>
cd comfyui-node-manager
Use code with caution.
Bash
2. 后端设置 (FastAPI)
后端负责所有核心逻辑，如扫描插件、解析依赖、执行 pip 命令等。
进入后端目录
cd backend
Use code with caution.
Bash
创建并激活 Python 虚拟环境 (推荐)
Windows:
python -m venv venv
venv\Scripts\activate
Use code with caution.
Cmd
Linux / macOS:
python3 -m venv venv
source venv/bin/activate
Use code with caution.
Bash
激活成功后，您的终端提示符前应出现 (venv)。
安装 Python 依赖
pip install -r requirements.txt
Use code with caution.
Bash
3. 前端设置 (Vue)
前端负责所有用户界面和交互。
打开一个新的终端，然后进入前端目录。
cd path/to/comfyui-node-manager/frontend
Use code with caution.
Bash
安装 Node.js 依赖
npm install
Use code with caution.
Bash
此命令会读取 package.json 文件并下载所有必需的前端库（如 Vue, Element Plus, Axios 等）。
🚀 启动项目
您需要同时启动后端和前端两个服务。请确保在两个独立的终端窗口中分别执行以下命令。
1. 启动后端服务
终端 1: 确保您位于 backend 目录并且 Python 虚拟环境已激活。
执行以下命令启动 FastAPI 开发服务器：
# 如果您使用的是 Windows
python run.py

# 如果您不使用 run.py，或者在非 Windows 系统上
#uvicorn app.main:app --port 8000

我们推荐使用 python run.py，因为它包含了对 Windows 平台的兼容性处理。
当您看到类似 Uvicorn running on http://127.0.0.1:8000 的输出时，表示后端已成功启动。
2. 启动前端服务
终端 2: 确保您位于 frontend 目录。
执行以下命令启动 Vite 开发服务器：
npm run dev

当您看到类似 Local: http://localhost:5173/ 的输出时，表示前端开发服务器已成功启动。
🖥️ 使用工具
访问应用
在您的浏览器中打开前端服务提供的地址，通常是：http://localhost:5173。
进行初次设置
程序首次打开时，请点击顶部的 设置 (Settings) 标签页。
填写 ComfyUI 插件目录路径 和 Python 解释器路径。这两个是必填项。
插件目录示例: D:\AI\ComfyUI\custom_nodes
Python 路径示例: D:\AI\ComfyUI\python_embeded\python.exe
根据需要选择一个 pip 镜像源以加快下载速度。
点击 [ 保存配置 ] 按钮。
开始管理依赖
切换回 管理器 (Manager) 标签页。
此时，界面应该会加载出您的插件列表和依赖信息。
您可以开始进行依赖检查、安装和更新等操作。详细操作请参考普通用户的使用说明。
❓ 开发常见问题
Q: 前端发起的 API 请求失败，浏览器控制台出现 CORS 跨域错误。
A: 请检查后端 backend/app/main.py 中的 CORSMiddleware 配置。确保 allow_origins 列表中包含了您的前端地址（如 http://localhost:5173）。
Q: 在 Windows 上安装依赖时，日志显示 NotImplementedError。
A: 这是因为 Windows 默认的 asyncio 事件循环策略不支持子进程。请确保您是通过 python run.py 来启动后端，或者在启动脚本中已经设置了 asyncio.WindowsProactorEventLoopPolicy()。
Q: 我修改了后端代码，但似乎没有生效。
A: 如果您是通过 uvicorn ... --reload 或 python run.py (内含 reload=True) 启动的，服务应该会自动重启。如果没生效，请尝试手动停止 (Ctrl+C) 并重新启动后端服务。
