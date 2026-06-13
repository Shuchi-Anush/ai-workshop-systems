import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

def replay_benchmarks():
    print("=========================================")
    print("   BENCHMARK REPLAY ENGINE               ")
    print("=========================================")
    
    # Ensure benchmark script exists
    script_path = Path("tests/retrieval_benchmarks/run_evaluations.py")
    if not script_path.exists():
        print(f"[FAIL] Cannot find {script_path}")
        sys.exit(1)
        
    print("[1] Executing benchmarks...")
    try:
        # Run the existing benchmark suite
        subprocess.run(["uv", "run", "python", str(script_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Benchmark execution failed: {e}")
        sys.exit(1)
        
    print("[2] Saving historical snapshot...")
    history_dir = Path("reports/benchmark_history")
    history_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_path = history_dir / f"snapshot_{timestamp}.json"
    
    leaderboard_path = Path("reports/retrieval_leaderboard.json")
    if leaderboard_path.exists():
        import shutil
        shutil.copy(leaderboard_path, snapshot_path)
        print(f"[OK] Snapshot saved to {snapshot_path}")
    else:
        print("[FAIL] Leaderboard output missing. Snapshot failed.")

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent.parent.parent)
    replay_benchmarks()
