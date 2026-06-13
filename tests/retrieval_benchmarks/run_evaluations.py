import os
import requests
import time
import json
import numpy as np
from pathlib import Path

API_URL = "http://127.0.0.1:8081"

def calc_mrr(expected, retrieved):
    for rank, rid in enumerate(retrieved, 1):
        if rid in expected: return 1.0 / rank
    return 0.0

def calc_precision_k(expected, retrieved, k):
    top_k = retrieved[:k]
    hits = sum(1 for rid in top_k if rid in expected)
    return hits / float(k)

def calc_recall_k(expected, retrieved, k):
    top_k = retrieved[:k]
    hits = sum(1 for rid in top_k if rid in expected)
    return hits / float(len(expected)) if expected else 0.0

def calc_ndcg_k(expected, retrieved, k):
    dcg = 0.0
    for i, rid in enumerate(retrieved[:k]):
        if rid in expected:
            dcg += 1.0 / np.log2(i + 2)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(expected), k)))
    return dcg / idcg if idcg > 0 else 0.0

def run_retrieval_benchmarks():
    print("=========================================")
    print("   PRODUCTION RETRIEVAL EVALUATION SUITE  ")
    print("=========================================\n")
    
    # 1. Wait for server
    for _ in range(15):
        try:
            requests.get(f"{API_URL}/api/v1/health")
            break
        except:
            time.sleep(1)
            
    # 2. Reset and Bulk Ingest the benchmark_ready dataset
    print("[1] Ingesting benchmark_ready dataset...")
    requests.post(f"{API_URL}/api/v1/reset-db?confirm=true")
    
    benchmark_dir = Path("datasets/processed/benchmark_ready")
    if not benchmark_dir.exists():
        print("Error: datasets/processed/benchmark_ready does not exist.")
        return
        
    files = []
    for category in ["golden", "distractors", "adversarial", "noisy"]:
        cat_dir = benchmark_dir / category
        if cat_dir.exists():
            for pdf_file in cat_dir.glob("*.pdf"):
                files.append(("files", (pdf_file.name, open(pdf_file, "rb"), "application/pdf")))
                
    if not files:
        print("No resumes found in benchmark_ready.")
        return
        
    start_ingest = time.time()
    res = requests.post(f"{API_URL}/api/v1/bulk-ingest", files=files).json()
    print(f"    Indexed {res.get('success_count')} resumes across {res.get('total_chunks')} chunks in {time.time()-start_ingest:.2f}s")
    
    golden_files = [f.stem.lower() for f in (benchmark_dir / "golden").glob("*.pdf")]
    adv_hr_stuffed = "adv_hr_keyword_stuffed"
    adv_fake_seniority = "adv_fake_seniority"
    
    # Test Cases
    test_cases = [
        {
            "query": "Senior Python Developer with FastAPI and Docker",
            "expected": golden_files,
            "anti_expected": [adv_hr_stuffed, adv_fake_seniority]
        },
        {
            "query": "React Frontend Developer with JavaScript",
            "expected": [f.stem.lower() for f in (benchmark_dir / "distractors").glob("*.pdf") if "react" in f.stem.lower()],
            "anti_expected": [adv_hr_stuffed]
        },
        {
            "query": "Senior C# Backend Engineer .NET Core",
            "expected": [f.stem.lower() for f in (benchmark_dir / "distractors").glob("*.pdf") if "c#" in f.stem.lower() or "dotnet" in f.stem.lower()],
            "anti_expected": golden_files + [adv_hr_stuffed]
        }
    ]
    
    print("\n[2] Running Evaluation Cases...")
    
    metrics = {"mrr": [], "p_at_3": [], "r_at_3": [], "ndcg_at_3": [], "latencies": [], "false_positives": 0}
    
    for tc in test_cases:
        start_eval = time.time()
        req = {"job_description": tc["query"], "top_k": 5}
        res = requests.post(f"{API_URL}/api/v1/evaluate", json=req).json()
        latency = (time.time() - start_eval) * 1000
        
        candidates = [c.get("candidate", {}).get("candidate_id") for c in res.get("candidates", [])]
        expected = [e for e in tc["expected"]]
        anti_expected = tc.get("anti_expected", [])
        
        # Calculate metrics
        mrr = calc_mrr(expected, candidates)
        p3 = calc_precision_k(expected, candidates, 3)
        r3 = calc_recall_k(expected, candidates, 3)
        ndcg3 = calc_ndcg_k(expected, candidates, 3)
        fps = sum(1 for c in candidates[:3] if c in anti_expected)
        
        metrics["mrr"].append(mrr)
        metrics["p_at_3"].append(p3)
        metrics["r_at_3"].append(r3)
        metrics["ndcg_at_3"].append(ndcg3)
        metrics["latencies"].append(latency)
        metrics["false_positives"] += fps
        
        print(f"\n  Query: {tc['query']}")
        print(f"  Lat: {latency:.1f}ms | MRR: {mrr:.2f} | P@3: {p3:.2f} | R@3: {r3:.2f} | NDCG@3: {ndcg3:.2f}")
        print(f"  Retrieved: {candidates}")
        if fps > 0:
            print(f"  [WARNING] False Positive Adversarial Hit: {[c for c in candidates if c in anti_expected]}")

    print("\n[3] Benchmark Summary")
    print(f"    Avg Latency:    {np.mean(metrics['latencies']):.1f}ms")
    print(f"    Mean MRR:       {np.mean(metrics['mrr']):.2f}")
    print(f"    Mean P@3:       {np.mean(metrics['p_at_3']):.2f}")
    print(f"    Mean R@3:       {np.mean(metrics['r_at_3']):.2f}")
    print(f"    Mean NDCG@3:    {np.mean(metrics['ndcg_at_3']):.2f}")
    print(f"    Total False Positives: {metrics['false_positives']} (Adversarial Leaks)")

    os.makedirs("reports", exist_ok=True)
    with open("reports/benchmark_metrics.json", "w") as f:
        json.dump({k: float(np.mean(v)) if isinstance(v, list) else v for k, v in metrics.items()}, f, indent=2)

if __name__ == "__main__":
    os.makedirs("tests/retrieval_benchmarks", exist_ok=True)
    run_retrieval_benchmarks()
