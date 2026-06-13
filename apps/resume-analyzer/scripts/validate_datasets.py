import os
import json
from pathlib import Path
import sqlite3

def validate_datasets():
    print("=========================================")
    print("   DATASET INTEGRITY VALIDATION ENGINE   ")
    print("=========================================")
    
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    report_lines = ["# Dataset Integrity Validation Report\n"]
    
    def log(msg, level="INFO"):
        print(f"[{level}] {msg}")
        report_lines.append(f"**{level}**: {msg}\n")

    # 1. Check directories
    raw_dir = Path("datasets/raw")
    processed_dir = Path("datasets/processed/benchmark_ready")
    
    if not processed_dir.exists():
        log("Processed benchmark directory missing.", "ERROR")
        return write_report(report_lines)
        
    pdfs = list(processed_dir.rglob("*.pdf"))
    if not pdfs:
        log("No PDF datasets found in benchmark_ready.", "ERROR")
    else:
        log(f"Found {len(pdfs)} benchmark resumes.", "INFO")
        
    # 2. Check Database consistency
    db_path = Path("apps/resume-analyzer/.data/chroma")
    if not db_path.exists():
        log("ChromaDB vector store not found.", "ERROR")
    else:
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(db_path))
            collection = client.get_collection("candidates")
            count = collection.count()
            log(f"ChromaDB Integrity: {count} embedded chunks found.", "INFO")
            
            # Check duplicate candidate IDs
            metadata = collection.get(include=["metadatas"])["metadatas"]
            if metadata:
                from collections import Counter
                candidates = [m.get("candidate_id") for m in metadata if m]
                dups = [c for c, cnt in Counter(candidates).items() if cnt > 50]
                if dups:
                    log(f"Found {len(dups)} candidates with an anomalous amount of chunks (>50).", "WARNING")
        except Exception as e:
            log(f"Database query failed: {e}", "ERROR")

    # 3. Manifest validation
    manifest_path = Path("datasets/manifests/query_suite.json")
    if not manifest_path.exists():
        log("query_suite.json manifest missing.", "WARNING")
    else:
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
            log(f"Manifest validated. Found {len(manifest.get('benchmark_queries', []))} queries.", "INFO")
        except Exception as e:
            log(f"Manifest invalid JSON: {e}", "ERROR")

    write_report(report_lines)
    print("\n[RESULT] Validation complete. Report generated at reports/dataset_validation_report.md")

def write_report(lines):
    with open("reports/dataset_validation_report.md", "w") as f:
        f.writelines(lines)

if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent.parent.parent)
    validate_datasets()
