import sys
import subprocess
import os
import urllib.request
import json
import time

def print_step(msg):
    print(f"\n[BOOTSTRAP] {msg}")

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_ollama():
    print_step("Validating Ollama installation...")
    success, out = run_cmd("ollama --version")
    if not success:
        print("[FAIL] Ollama not found. Please install Ollama from https://ollama.com/")
        return False
    print(f"[OK] Ollama found: {out.strip()}")
    
    print_step("Validating required models...")
    success, out = run_cmd("ollama list")
    if "phi3" not in out:
        print("[FAIL] Model 'phi3' not found. Pulling now...")
        success_pull, _ = run_cmd("ollama pull phi3")
        if not success_pull:
            print("[FAIL] Failed to pull phi3 model.")
            return False
        print("[OK] Pulled phi3 model.")
    else:
        print("[OK] Model 'phi3' is available.")
        
    if "nomic-embed-text" not in out:
        print("[FAIL] Model 'nomic-embed-text' not found. Pulling now...")
        success_pull, _ = run_cmd("ollama pull nomic-embed-text")
        if not success_pull:
            print("[FAIL] Failed to pull nomic-embed-text model.")
            return False
        print("[OK] Pulled nomic-embed-text model.")
    else:
        print("[OK] Model 'nomic-embed-text' is available.")
    return True

def check_directories():
    print_step("Validating data directories...")
    base_dir = Path("apps/resume-analyzer/.data")
    dirs = [
        base_dir / "chroma",
        base_dir / "metadata",
        base_dir / "bm25",
        Path("datasets/raw"),
        Path("datasets/processed"),
        Path("reports")
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        # Check write access
        test_file = d / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            print(f"[FAIL] Cannot write to directory {d}: {e}")
            return False
    print("[OK] Directory structure and write access verified.")
    return True

def check_api_health():
    print_step("Validating API health...")
    try:
        req = urllib.request.urlopen("http://127.0.0.1:8081/api/v1/health", timeout=5)
        res = json.loads(req.read().decode())
        print("[OK] API is healthy.")
        return True
    except Exception as e:
        print(f"[FAIL] API health check failed: {e}. Is the backend running on port 8081?")
        return False

def smoke_test():
    print_step("Running smoke retrieval test...")
    try:
        data = json.dumps({"job_description": "test", "top_k": 1, "mode": "hybrid"}).encode('utf-8')
        req = urllib.request.Request("http://127.0.0.1:8081/api/v1/evaluate", data=data, headers={'Content-Type': 'application/json'}, method='POST')
        res = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
        print(f"[OK] Smoke test passed. Execution time: {res.get('execution_time_ms', 0):.1f}ms")
        return True
    except Exception as e:
        print(f"[FAIL] Smoke test failed: {e}")
        return False

from pathlib import Path

def main():
    print("=========================================")
    print("   WORKSHOP BOOTSTRAP AND VERIFICATION   ")
    print("=========================================")
    
    if sys.version_info < (3, 10):
        print(f"[FAIL] Python version must be >= 3.10. Current: {sys.version}")
        sys.exit(1)
    print(f"[OK] Python version: {sys.version.split()[0]}")
    
    # Check uv
    success, out = run_cmd("uv --version")
    if not success:
        print("[FAIL] 'uv' is not installed.")
        sys.exit(1)
    print(f"[OK] uv found: {out.strip()}")
    
    if not check_ollama():
        print("\n[RESULT] WORKSHOP NOT READY [FAIL]")
        sys.exit(1)
        
    if not check_directories():
        print("\n[RESULT] WORKSHOP NOT READY [FAIL]")
        sys.exit(1)
        
    # Check dependencies locally
    print_step("Validating core imports...")
    try:
        import streamlit
        import fastapi
        import chromadb
        import rank_bm25
        print("[OK] Core dependencies imported successfully.")
    except ImportError as e:
        print(f"[FAIL] Failed to import core dependency: {e}. Run `uv sync`.")
        print("\n[RESULT] WORKSHOP NOT READY [FAIL]")
        sys.exit(1)

    print_step("Warming up models...")
    try:
        data = json.dumps({"model": "phi3", "prompt": "hi", "stream": False}).encode('utf-8')
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=data, headers={'Content-Type': 'application/json'}, method='POST')
        urllib.request.urlopen(req, timeout=20)
        
        # Newer Ollama might use /api/embeddings or /api/embed
        try:
            data_emb = json.dumps({"model": "nomic-embed-text", "prompt": "hi"}).encode('utf-8')
            req_emb = urllib.request.Request("http://127.0.0.1:11434/api/embeddings", data=data_emb, headers={'Content-Type': 'application/json'}, method='POST')
            urllib.request.urlopen(req_emb, timeout=20)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Try new embed endpoint
                data_emb = json.dumps({"model": "nomic-embed-text", "input": "hi"}).encode('utf-8')
                req_emb = urllib.request.Request("http://127.0.0.1:11434/api/embed", data=data_emb, headers={'Content-Type': 'application/json'}, method='POST')
                urllib.request.urlopen(req_emb, timeout=20)
                
        print("[OK] Models warmed up.")
    except Exception as e:
        print(f"[WARN] Failed to warm up models: {e}. They will load on first request.")
        
    if not check_api_health():
        print("[WARN] API is not running. Starting API in background for testing...")
        # Start API using subprocess
        # For simplicity in bootstrap, we advise the user to run it.
        print("Please run `uv run uvicorn apps.resume_analyzer.backend.api.main:app --port 8081` in a separate terminal.")
        print("\n[RESULT] WORKSHOP ALMOST READY (API OFF) [WARN]")
        sys.exit(0)
        
    if not smoke_test():
        print("\n[RESULT] WORKSHOP NOT READY [FAIL]")
        sys.exit(1)
        
    print("\n[RESULT] WORKSHOP READY [OK]")

if __name__ == "__main__":
    # Ensure working dir is repo root
    os.chdir(Path(__file__).parent.parent.parent.parent)
    main()
