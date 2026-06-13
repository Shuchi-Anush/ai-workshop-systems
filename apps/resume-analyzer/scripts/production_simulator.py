import requests
import time
import random
import sys

API_URL = "http://127.0.0.1:8081"

queries = [
    "Senior Python Developer with FastAPI and Docker",
    "React Frontend Developer with JavaScript",
    "Senior C# Backend Engineer .NET Core",
    "Data Engineer PySpark AWS",
    "Machine Learning Engineer PyTorch"
]

modes = ["dense", "sparse", "hybrid"]

def print_step(msg):
    print(f"\n[SIMULATOR] {msg}")

def simulate():
    print_step("Starting Production Stress Simulation...")
    print_step("Target: 100 concurrent-like searches across dense, sparse, and hybrid modes.")
    
    success = 0
    fail = 0
    start_time = time.time()
    
    for i in range(1, 101):
        q = random.choice(queries)
        m = random.choice(modes)
        
        try:
            t0 = time.time()
            res = requests.post(f"{API_URL}/api/v1/evaluate", json={
                "job_description": q,
                "top_k": 3,
                "mode": m
            }, timeout=5)
            t1 = time.time()
            
            if res.status_code == 200:
                success += 1
                lat = (t1 - t0) * 1000
                print(f"[{i}/100] [OK] Mode: {m.upper():<6} | Latency: {lat:.1f}ms | Query: {q[:20]}...")
            else:
                fail += 1
                print(f"[{i}/100] [FAIL] HTTP {res.status_code}")
                
        except Exception as e:
            fail += 1
            print(f"[{i}/100] [ERROR] {e}")
            
    total_time = time.time() - start_time
    print_step("Simulation Complete")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Success: {success}")
    print(f"Failures: {fail}")
    print(f"Avg Latency: {(total_time / 100) * 1000:.1f}ms")
    
if __name__ == "__main__":
    simulate()
