import os
import requests
import time
from pathlib import Path

API_URL = "http://127.0.0.1:8081"

def calculate_mrr(expected_ids: list[str], retrieved_ids: list[str]) -> float:
    for rank, rid in enumerate(retrieved_ids, 1):
        if rid in expected_ids:
            return 1.0 / rank
    return 0.0

def calculate_precision_at_k(expected_ids: list[str], retrieved_ids: list[str], k: int) -> float:
    retrieved_k = retrieved_ids[:k]
    hits = sum(1 for rid in retrieved_k if rid in expected_ids)
    return hits / float(k)

def calculate_recall_at_k(expected_ids: list[str], retrieved_ids: list[str], k: int) -> float:
    retrieved_k = retrieved_ids[:k]
    hits = sum(1 for rid in retrieved_k if rid in expected_ids)
    return hits / float(len(expected_ids)) if expected_ids else 0.0

def run_benchmark():
    print("======================================")
    print("      RESUME RETRIEVAL BENCHMARK      ")
    print("======================================\n")
    
    # 1. Wait for server
    for _ in range(15):
        try:
            requests.get(f"{API_URL}/health")
            break
        except requests.ConnectionError:
            time.sleep(1)
            
    # 2. Reset DB
    requests.post(f"{API_URL}/api/v1/reset-db?confirm=true")
    
    # 3. Bulk Ingest
    print("[1] Ingesting test corpus...")
    resumes_dir = Path("tests/benchmark/resumes")
    files = []
    for pdf_file in resumes_dir.glob("*.pdf"):
        files.append(("files", (pdf_file.name, open(pdf_file, "rb"), "application/pdf")))
        
    start_ingest = time.time()
    ingest_res = requests.post(f"{API_URL}/api/v1/bulk-ingest", files=files).json()
    ingest_time = time.time() - start_ingest
    print(f"    Indexed {ingest_res.get('success_count', 0)} resumes in {ingest_time:.2f}s")
    
    # 4. Define Test Cases
    test_cases = [
        {
            "name": "Python Developer Search",
            "query": "Looking for a Senior Python Developer with FastAPI and Docker experience.",
            "expected_top": ["golden_python_dev"]
        },
        {
            "name": "C# Developer Search",
            "query": "Need a backend engineer strong in C# and .NET core.",
            "expected_top": ["distractor_csharp_dev"]
        },
        {
            "name": "Frontend React Search",
            "query": "Frontend developer proficient in React and JavaScript.",
            "expected_top": ["distractor_react_dev"]
        }
    ]
    
    # 5. Execute Evaluation
    all_mrrs = []
    print("\n[2] Executing Search Evaluations...")
    for tc in test_cases:
        start_eval = time.time()
        eval_req = {"job_description": tc["query"], "top_k": 3}
        eval_res = requests.post(f"{API_URL}/api/v1/evaluate", json=eval_req).json()
        latency = (time.time() - start_eval) * 1000
        
        candidates = eval_res.get("candidates", [])
        retrieved_ids = [c.get("candidate", {}).get("candidate_id") for c in candidates]
        
        mrr = calculate_mrr(tc["expected_top"], retrieved_ids)
        p_at_1 = calculate_precision_at_k(tc["expected_top"], retrieved_ids, 1)
        r_at_3 = calculate_recall_at_k(tc["expected_top"], retrieved_ids, 3)
        all_mrrs.append(mrr)
        
        print(f"  - Case: {tc['name']}")
        print(f"    Lat: {latency:.1f}ms | MRR: {mrr:.2f} | P@1: {p_at_1:.2f} | R@3: {r_at_3:.2f}")
        print(f"    Retrieved: {retrieved_ids}")
        assert mrr >= 0.5, f"Retrieval completely failed for {tc['name']}"
        assert latency < 2000, f"Latency too high: {latency}ms"

    print("\n[3] System State Validation...")
    stats = requests.get(f"{API_URL}/api/v1/stats").json()
    assert stats["total_candidates"] == 3, "Persistence mismatch"
    print(f"    Persistence Validated: {stats['total_candidates']} Candidates.")

    print(f"\n[PASS] All {len(test_cases)} benchmarks passed! System is stable.")

if __name__ == "__main__":
    run_benchmark()
