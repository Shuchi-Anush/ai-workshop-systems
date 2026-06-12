import os
import shutil
from pathlib import Path

repo_root = Path("d:/ai-workshop-systems")

moves = [
    {
        "src": repo_root / "shared" / "schemas" / "vector.py",
        "dest": repo_root / "packages" / "ai-vector" / "src" / "ai_vector" / "schemas" / "vector.py",
        "old_import": "shared.schemas.vector",
        "new_import": "ai_vector.schemas.vector",
        "shim_content": "from ai_vector.schemas.vector import *\\n"
    },
    {
        "src": repo_root / "shared" / "pipelines" / "base.py",
        "dest": repo_root / "packages" / "ai-observability" / "src" / "ai_observability" / "pipelines" / "base.py",
        "old_import": "shared.pipelines.base",
        "new_import": "ai_observability.pipelines.base",
        "shim_content": "from ai_observability.pipelines.base import *\\n"
    },
    {
        "src": repo_root / "shared" / "mocks" / "mock_embedder.py",
        "dest": repo_root / "packages" / "ai-testing" / "src" / "ai_testing" / "mocks" / "mock_embedder.py",
        "old_import": "shared.mocks.mock_embedder",
        "new_import": "ai_testing.mocks.mock_embedder",
        "shim_content": "from ai_testing.mocks.mock_embedder import *\\n"
    },
    {
        "src": repo_root / "shared" / "mocks" / "mock_vectordb.py",
        "dest": repo_root / "packages" / "ai-testing" / "src" / "ai_testing" / "mocks" / "mock_vectordb.py",
        "old_import": "shared.mocks.mock_vectordb",
        "new_import": "ai_testing.mocks.mock_vectordb",
        "shim_content": "from ai_testing.mocks.mock_vectordb import *\\n"
    }
]

search_dirs = [
    repo_root / "shared",
    repo_root / "task_01_resume_rag",
    repo_root / "tests"
]

modified_files = set()

for move in moves:
    src_path = move["src"]
    dest_path = move["dest"]
    
    # Ensure dest parent exists and contains __init__.py
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    (dest_path.parent / "__init__.py").touch()
    
    # Move file if it exists (might have been moved in a previous test)
    if src_path.exists() and not dest_path.exists():
        shutil.move(str(src_path), str(dest_path))
    
    # Create shim
    with open(src_path, "w") as f:
        f.write(move["shim_content"])
        
    # Rewrite safe consumers
    old_import = move["old_import"]
    new_import = move["new_import"]
    
    for d in search_dirs:
        for filepath in d.rglob("*.py"):
            # Do not rewrite the shim itself!
            if str(filepath) == str(src_path):
                continue
                
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                new_content = content
                new_content = new_content.replace(f"from {old_import}", f"from {new_import}")
                new_content = new_content.replace(f"import {old_import}", f"import {new_import}")
                
                if new_content != content:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    modified_files.add(str(filepath.relative_to(repo_root)))
            except Exception as e:
                pass

print("Extraction Complete")
for mf in modified_files:
    print(f"Rewrote: {mf}")
