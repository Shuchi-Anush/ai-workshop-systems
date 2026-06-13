import os
import ast
import sys
from typing import List, Tuple

def get_python_files(root_dir: str) -> List[str]:
    files = []
    for dirpath, _, filenames in os.walk(root_dir):
        if "venv" in dirpath or ".venv" in dirpath or "__pycache__" in dirpath:
            continue
        for f in filenames:
            if f.endswith(".py"):
                files.append(os.path.join(dirpath, f))
    return files

def get_imports(filepath: str) -> List[str]:
    imports = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except Exception as e:
        print(f"Warning: Failed to parse {filepath}: {e}")
    return imports

def check_boundaries() -> bool:
    print("=== MONOREPO GOVERNANCE SCAN ===")
    
    apps_dir = "apps"
    packages_dir = "packages"
    
    if not os.path.exists(apps_dir) or not os.path.exists(packages_dir):
        print("Error: Run this script from the monorepo root.")
        return False
        
    violations = []
    
    # 1. Packages should not import from apps
    package_files = get_python_files(packages_dir)
    for p_file in package_files:
        imports = get_imports(p_file)
        for imp in imports:
            if imp.startswith("apps."):
                violations.append((p_file, imp, "Package importing from App"))
                
    # 2. Apps should not import from other apps (except themselves)
    # Get list of app namespaces
    app_namespaces = []
    for item in os.listdir(apps_dir):
        if os.path.isdir(os.path.join(apps_dir, item)):
            # convert folder name to import namespace format (replace - with _)
            app_namespaces.append(item.replace("-", "_"))
            
    app_files = get_python_files(apps_dir)
    for a_file in app_files:
        # Determine which app this file belongs to
        # e.g. apps/resume-analyzer/src/...
        parts = a_file.split(os.sep)
        if len(parts) > 1:
            current_app = parts[1].replace("-", "_")
            
            imports = get_imports(a_file)
            for imp in imports:
                if imp.startswith("apps."):
                    # e.g. apps.resume_analyzer...
                    target_app = imp.split(".")[1]
                    if target_app != current_app and target_app in app_namespaces:
                        violations.append((a_file, imp, f"App '{current_app}' importing from App '{target_app}'"))
                        
    if violations:
        print(f"\n[FAIL] Found {len(violations)} architectural violations:\n")
        for filepath, import_stmt, reason in violations:
            print(f"  {reason}")
            print(f"    File:   {filepath}")
            print(f"    Import: {import_stmt}\n")
        return False
        
    print("[PASS] Monorepo boundaries are pure. No cyclic or upward imports detected.")
    return True

if __name__ == "__main__":
    success = check_boundaries()
    if not success:
        sys.exit(1)
    sys.exit(0)
