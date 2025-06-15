from pydantic import BaseModel
from typing import List, Optional

class Config(BaseModel):
    comfyui_path: str
    python_path: str
    pip_mirror: str

class PluginInfo(BaseModel):
    name: str
    has_reqs: bool

class InstalledPackage(BaseModel):
    name: str
    version: str

class PackageInstallRequest(BaseModel):
    package_name: str
    mirror_url: Optional[str] = None