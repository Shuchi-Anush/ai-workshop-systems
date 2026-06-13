import json
import os
from collections import Counter

def generate_taxonomy():
    try:
        with open("reports/retrieval_failures.json", "r") as f:
            failures = json.load(f)
    except Exception as e:
        print(f"Error loading failures: {e}")
        return

    taxonomy_counts = Counter()
    detailed_failures = []
    
    for mode, mode_failures in failures.items():
        for f in mode_failures:
            reasons = []
            fps = f.get("fps", [])
            retrieved = f.get("retrieved", [])
            expected = f.get("expected", [])
            
            # Identify root cause
            if "adv_hr_keyword_stuffed" in fps:
                reasons.append("Keyword Stuffing")
            if "adv_fake_seniority" in fps:
                reasons.append("Seniority Inflation")
                
            if len([e for e in expected if e not in retrieved[:3]]) > 0:
                if mode == "dense":
                    reasons.append("Dense Similarity Collapse")
                elif mode == "sparse":
                    reasons.append("Sparse Mismatch")
                elif mode == "hybrid":
                    reasons.append("Hybrid Dilution")
            
            if not reasons:
                reasons.append("Semantic Bleed")
                
            for r in reasons:
                taxonomy_counts[r] += 1
                
            detailed_failures.append({
                "query": f["query"],
                "mode": mode,
                "reasons": reasons,
                "leak_sources": fps,
                "retrieved": retrieved[:3]
            })
            
    taxonomy_report = {
        "summary": dict(taxonomy_counts),
        "details": detailed_failures
    }
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/retrieval_failure_taxonomy.json", "w") as f:
        json.dump(taxonomy_report, f, indent=2)
        
    with open("reports/retrieval_failure_taxonomy.md", "w") as f:
        f.write("# Retrieval Failure Taxonomy\n\n")
        f.write("## Summary\n\n")
        for reason, count in taxonomy_counts.items():
            f.write(f"- **{reason}**: {count} occurrences\n")
            
        f.write("\n## Detailed Failures\n\n")
        for d in detailed_failures:
            f.write(f"### Query: `{d['query']}` ({d['mode'].upper()})\n")
            f.write(f"- **Root Cause(s)**: {', '.join(d['reasons'])}\n")
            if d['leak_sources']:
                f.write(f"- **Adversarial Leaks**: {', '.join(d['leak_sources'])}\n")
            f.write(f"- **Top Retrieved**: {', '.join(d['retrieved'])}\n\n")
            
if __name__ == "__main__":
    generate_taxonomy()
