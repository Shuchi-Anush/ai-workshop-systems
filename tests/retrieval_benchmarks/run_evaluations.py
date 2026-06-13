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
    print("   RETRIEVAL LEADERBOARD BENCHMARK SUITE ")
    print("=========================================\n")
    
    # 1. Wait for server
    for _ in range(15):
        try:
            requests.get(f"{API_URL}/api/v1/health")
            break
        except:
            time.sleep(1)
            
    # 2. Setup Test Cases
    benchmark_dir = Path("datasets/processed/benchmark_ready")
    golden_files = [f.stem.lower() for f in (benchmark_dir / "golden").glob("*.pdf")]
    adv_hr_stuffed = "adv_hr_keyword_stuffed"
    adv_fake_seniority = "adv_fake_seniority"
    
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
    
    modes = ["dense", "sparse", "hybrid"]
    results = {mode: {"mrr": [], "p_at_3": [], "r_at_3": [], "ndcg_at_3": [], "latencies": [], "false_positives": 0, "failures": []} for mode in modes}
    
    print("[1] Running Evaluation Cases across Dense, Sparse, Hybrid...\n")
    
    for mode in modes:
        print(f"--- MODE: {mode.upper()} ---")
        for tc in test_cases:
            start_eval = time.time()
            req = {"job_description": tc["query"], "top_k": 5, "mode": mode}
            res = requests.post(f"{API_URL}/api/v1/evaluate", json=req).json()
            latency = (time.time() - start_eval) * 1000
            
            candidates = [c.get("candidate", {}).get("candidate_id") for c in res.get("candidates", [])]
            expected = [e for e in tc["expected"]]
            anti_expected = tc.get("anti_expected", [])
            
            mrr = calc_mrr(expected, candidates)
            p3 = calc_precision_k(expected, candidates, 3)
            r3 = calc_recall_k(expected, candidates, 3)
            ndcg3 = calc_ndcg_k(expected, candidates, 3)
            fps = sum(1 for c in candidates[:3] if c in anti_expected)
            
            results[mode]["mrr"].append(mrr)
            results[mode]["p_at_3"].append(p3)
            results[mode]["r_at_3"].append(r3)
            results[mode]["ndcg_at_3"].append(ndcg3)
            results[mode]["latencies"].append(latency)
            results[mode]["false_positives"] += fps
            
            # Record failures for Phase 2
            if r3 < 1.0 or fps > 0:
                results[mode]["failures"].append({
                    "query": tc["query"],
                    "mode": mode,
                    "retrieved": candidates,
                    "expected": expected,
                    "fps": [c for c in candidates[:3] if c in anti_expected]
                })
                
            print(f"  Query: {tc['query']}")
            print(f"  Lat: {latency:.1f}ms | MRR: {mrr:.2f} | R@3: {r3:.2f} | FPs: {fps}")
        print()

    print("\n[2] Benchmark Leaderboard Summary")
    
    leaderboard = {}
    for mode in modes:
        leaderboard[mode] = {
            "Avg Latency (ms)": float(np.mean(results[mode]["latencies"])),
            "Mean MRR": float(np.mean(results[mode]["mrr"])),
            "Mean P@3": float(np.mean(results[mode]["p_at_3"])),
            "Mean R@3": float(np.mean(results[mode]["r_at_3"])),
            "Mean NDCG@3": float(np.mean(results[mode]["ndcg_at_3"])),
            "Total False Positives": results[mode]["false_positives"]
        }
        print(f"  [{mode.upper()}] MRR: {leaderboard[mode]['Mean MRR']:.2f} | R@3: {leaderboard[mode]['Mean R@3']:.2f} | FPs: {leaderboard[mode]['Total False Positives']} | Lat: {leaderboard[mode]['Avg Latency (ms)']:.1f}ms")

    os.makedirs("reports", exist_ok=True)
    with open("reports/retrieval_leaderboard.json", "w") as f:
        json.dump(leaderboard, f, indent=2)
        
    with open("reports/retrieval_leaderboard.md", "w") as f:
        f.write("# Retrieval Leaderboard\n\n")
        f.write("| Mode | MRR | P@3 | R@3 | NDCG@3 | False Positives | Avg Latency |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for mode in modes:
            m = leaderboard[mode]
            f.write(f"| {mode.upper()} | {m['Mean MRR']:.3f} | {m['Mean P@3']:.3f} | {m['Mean R@3']:.3f} | {m['Mean NDCG@3']:.3f} | {m['Total False Positives']} | {m['Avg Latency (ms)']:.1f}ms |\n")
            
    with open("reports/retrieval_failures.json", "w") as f:
        failures = {mode: results[mode]["failures"] for mode in modes}
        json.dump(failures, f, indent=2)
        
    print("\nLeaderboard generated in reports/retrieval_leaderboard.md")

if __name__ == "__main__":
    os.makedirs("tests/retrieval_benchmarks", exist_ok=True)
    run_retrieval_benchmarks()
