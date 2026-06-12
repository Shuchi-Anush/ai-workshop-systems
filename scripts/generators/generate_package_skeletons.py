import os
from pathlib import Path

base_dir = Path("d:/ai-workshop-systems/packages")
base_dir.mkdir(parents=True, exist_ok=True)

packages = [
    "ai-contracts",
    "ai-vector",
    "ai-testing",
    "ai-observability",
    "ai-errors"
]

for pkg in packages:
    pkg_dir = base_dir / pkg
    src_dir = pkg_dir / "src" / pkg.replace("-", "_")
    src_dir.mkdir(parents=True, exist_ok=True)
    
    # __init__.py
    (src_dir / "__init__.py").touch()
    
    # README.md
    with open(pkg_dir / "README.md", "w") as f:
        f.write(f"# {pkg}\\n\\nInternal AI Platform package for {pkg}.\\n")
        
    # pyproject.toml
    with open(pkg_dir / "pyproject.toml", "w") as f:
        f.write(f'''[project]
name = "{pkg}"
version = "0.1.0"
description = "Internal package for {pkg}"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0.0"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
''')

print("Successfully created package skeletons.")
