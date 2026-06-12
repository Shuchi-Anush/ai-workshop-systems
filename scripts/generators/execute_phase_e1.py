import os
from pathlib import Path

repo_root = Path("d:/ai-workshop-systems")
app_root = repo_root / "apps/resume-analyzer"

def create_skeleton():
    # Directories
    dirs = [
        app_root / "src/apps/resume_analyzer/backend",
        app_root / "frontend",
        app_root / "tests/integration",
        app_root / "tests/fixtures"
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        # Create __init__.py in all python packages
        if "src" in str(d):
            curr = d
            while curr != app_root / "src":
                (curr / "__init__.py").touch()
                curr = curr.parent
        if "tests" in str(d):
            (d / "__init__.py").touch()

    # pyproject.toml
    pyproject_content = """[project]
name = "resume-analyzer"
version = "0.1.0"
requires-python = ">=3.11,<3.12"
dependencies = [
    "ai-contracts",
    "ai-vector",
    "ai-observability",
    "ai-testing",
    "fastapi",
    "pydantic",
    "pytest"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
    (app_root / "pyproject.toml").write_text(pyproject_content, encoding="utf-8")
    
    # README.md
    readme_content = """# Resume Analyzer
    
Core backend application for the Resume Analysis system.
"""
    (app_root / "README.md").write_text(readme_content, encoding="utf-8")
    
    # Update root pyproject.toml
    root_pyproject = repo_root / "pyproject.toml"
    content = root_pyproject.read_text(encoding="utf-8")
    if '"apps/*"' not in content:
        # Check if members exists
        if 'members = ["packages/*"]' in content:
            content = content.replace('members = ["packages/*"]', 'members = ["packages/*", "apps/*"]')
        else:
            print("Could not automatically update root pyproject.toml workspace members.")
        root_pyproject.write_text(content, encoding="utf-8")

if __name__ == "__main__":
    create_skeleton()
    print("Wave E1 Complete")
