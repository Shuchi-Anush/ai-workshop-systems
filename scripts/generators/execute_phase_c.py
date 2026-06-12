import os
import glob
import shutil
from pathlib import Path

repo_root = Path("d:/ai-workshop-systems")

src_interfaces = repo_root / "shared" / "interfaces"
src_common = repo_root / "shared" / "schemas" / "common.py"

dest_interfaces = repo_root / "packages" / "ai-contracts" / "src" / "ai_contracts" / "interfaces"
dest_schemas = repo_root / "packages" / "ai-contracts" / "src" / "ai_contracts" / "schemas"

# 1. Ensure target directories exist
dest_interfaces.mkdir(parents=True, exist_ok=True)
dest_schemas.mkdir(parents=True, exist_ok=True)
(dest_interfaces / "__init__.py").touch()
(dest_schemas / "__init__.py").touch()

# 2. Move interfaces
interface_files = list(src_interfaces.glob("*.py"))
for f in interface_files:
    if f.is_file():
        shutil.move(str(f), str(dest_interfaces / f.name))
        
        # Create compatibility shim
        with open(f, "w") as shim:
            shim.write(f"# Transitional compatibility shim\\n")
            if f.name != "__init__.py":
                module_name = f.stem
                shim.write(f"from ai_contracts.interfaces.{module_name} import *\\n")

# 3. Move common.py
if src_common.exists():
    shutil.move(str(src_common), str(dest_schemas / "common.py"))
    # Create compatibility shim
    with open(src_common, "w") as shim:
        shim.write(f"# Transitional compatibility shim\\n")
        shim.write(f"from ai_contracts.schemas.common import *\\n")

# 4. Rewrite imports
# We will search through .py files in shared/, task_01_resume_rag/, tests/
search_dirs = [
    repo_root / "shared",
    repo_root / "task_01_resume_rag",
    repo_root / "tests"
]

replacements = {
    "from shared.interfaces": "from ai_contracts.interfaces",
    "import shared.interfaces": "import ai_contracts.interfaces",
    "from shared.schemas.common": "from ai_contracts.schemas.common",
    "import shared.schemas.common": "import ai_contracts.schemas.common"
}

modified_files = []

for d in search_dirs:
    for filepath in d.rglob("*.py"):
        # Don't rewrite the shims themselves!
        if filepath.parent == src_interfaces or filepath == src_common:
            continue
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = content
            for old_str, new_str in replacements.items():
                new_content = new_content.replace(old_str, new_str)
                
            if new_content != content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                modified_files.append(str(filepath.relative_to(repo_root)))
        except Exception as e:
            print(f"Failed to process {filepath}: {e}")

print("--- Extraction Complete ---")
print(f"Moved {len(interface_files)} interface files.")
print("Moved common.py.")
print(f"Rewrote imports in {len(modified_files)} files.")
for mf in modified_files:
    print(f"  - {mf}")
