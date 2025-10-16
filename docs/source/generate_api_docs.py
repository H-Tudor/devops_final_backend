import os
import shutil
import subprocess
from pathlib import Path

initial_path = Path(__file__).parent
pkg_dir = initial_path.parent.parent / "src" / "devops_final_backend"
api_dir = initial_path / "api"

if api_dir.exists():
    shutil.rmtree(api_dir)

os.makedirs(api_dir, exist_ok=True)

subprocess.run([
    "sphinx-apidoc",
    "-o", api_dir,
    pkg_dir,
    "--force",
], check=True)