import os
import shutil
from pathlib import Path
import urllib.request
import json

def print_step(msg):
    print(f"[REPAIR] {msg}")

def repair_environment():
    print("=========================================")
    print("   ENVIRONMENT REPAIR & RESTORE TOOL     ")
    print("=========================================")
    
    base_dir = Path("apps/resume-analyzer/.data")
    
    # 1. Clear corrupted vector stores
    print_step("Wiping ChromaDB vector store...")
    chroma_dir = base_dir / "chroma"
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)
        print("[OK] Chroma directory cleared.")
        
    # 2. Reset SQLite state
    print_step("Wiping SQLite metadata and BM25 store...")
    meta_dir = base_dir / "metadata"
    bm25_dir = base_dir / "bm25"
    if meta_dir.exists(): shutil.rmtree(meta_dir)
    if bm25_dir.exists(): shutil.rmtree(bm25_dir)
    print("[OK] Metadata and BM25 directories cleared.")
    
    # 3. Recreate base folders
    print_step("Recreating empty structure...")
    chroma_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)
    bm25_dir.mkdir(parents=True, exist_ok=True)
    print("[OK] Base directories restored.")
    
    # 4. Trigger bulk ingest
    print_step("Triggering API to rebuild BM25 and Chroma indexes...")
    try:
        # Check if API is up
        req = urllib.request.urlopen("http://127.0.0.1:8081/api/v1/health", timeout=5)
        
        benchmark_dir = Path("datasets/processed/benchmark_ready")
        if benchmark_dir.exists():
            print("  Running tests/retrieval_benchmarks/run_evaluations.py which handles bulk ingest...")
            import subprocess
            subprocess.run(["uv", "run", "python", "tests/retrieval_benchmarks/run_evaluations.py"], check=True)
            print("[OK] Environment successfully repaired and benchmarks restored.")
        else:
            print("[WARN] datasets/processed/benchmark_ready missing. Could not re-ingest.")
    except Exception as e:
        print(f"[WARN] API is down ({e}). Cannot rebuild indexes. Please start the backend and run `uv run python tests/retrieval_benchmarks/run_evaluations.py` manually.")

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent.parent.parent)
    repair_environment()
