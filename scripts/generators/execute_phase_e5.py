import os
import shutil
from pathlib import Path

repo_root = Path("d:/ai-workshop-systems")
src_base = repo_root / "task_01_resume_rag/src"
dest_base = repo_root / "apps/resume-analyzer/src/apps/resume_analyzer/backend"

directories_to_move = ["parser", "rag", "ranking", "services", "utils"]

for dir_name in directories_to_move:
    src_dir = src_base / dir_name
    dest_dir = dest_base / dir_name
    
    # Move directory content or just create empty ones if they exist
    if src_dir.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
        for item in src_dir.iterdir():
            if item.is_file() and item.suffix == ".py":
                dest_file = dest_dir / item.name
                shutil.copy2(item, dest_file)
                # Create shim in the source file
                module_name = item.stem
                if module_name == "__init__":
                    item.write_text(f"from apps.resume_analyzer.backend.{dir_name} import *\n", encoding="utf-8")
                else:
                    item.write_text(f"from apps.resume_analyzer.backend.{dir_name}.{module_name} import *\n", encoding="utf-8")
            elif item.is_dir() and item.name != "__pycache__":
                shutil.copytree(item, dest_dir / item.name, dirs_exist_ok=True)
                # Not creating deep shims for now as it's mostly flat
                shutil.rmtree(item)

# Also rewrite imports in tests or shared if any pointed to task_01_resume_rag.src
# But earlier grep showed none, only domain.py had an import.
# domain.py is already shimmed.

print("Wave E5 script executed successfully.")
