import os
import argparse
import requests
import time

def load_dataset(dataset_path: str, api_url: str, batch_size: int = 5):
    """Recursively discover PDFs and upload them to /bulk-ingest in batches."""
    print(f"Scanning directory: {dataset_path}")
    
    pdf_files = []
    for root, _, files in os.walk(dataset_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
                
    print(f"Found {len(pdf_files)} PDFs.")
    if not pdf_files:
        print("No PDFs found. Exiting.")
        return

    success_total = 0
    failure_total = 0
    start_time = time.time()

    # Process in batches
    for i in range(0, len(pdf_files), batch_size):
        batch = pdf_files[i:i+batch_size]
        print(f"Uploading batch {i//batch_size + 1} ({len(batch)} files)...")
        
        # Prepare multipart form data
        files_payload = []
        file_handles = []
        try:
            for filepath in batch:
                f = open(filepath, "rb")
                file_handles.append(f)
                files_payload.append(("files", (os.path.basename(filepath), f, "application/pdf")))
            
            response = requests.post(f"{api_url}/bulk-ingest", files=files_payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Success: {result['success_count']}, Failures: {result['failure_count']}, Chunks: {result['total_chunks']}")
                success_total += result['success_count']
                failure_total += result['failure_count']
            else:
                print(f"  Batch failed with HTTP {response.status_code}: {response.text}")
                failure_total += len(batch)
        except Exception as e:
            print(f"  Error uploading batch: {e}")
            failure_total += len(batch)
        finally:
            for f in file_handles:
                f.close()
                
    end_time = time.time()
    print("\n--- Ingestion Summary ---")
    print(f"Total files discovered: {len(pdf_files)}")
    print(f"Successfully ingested: {success_total}")
    print(f"Failed to ingest: {failure_total}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk ingest resume dataset.")
    parser.add_argument("--path", type=str, default="data/resumes/", help="Directory containing PDFs to ingest.")
    parser.add_argument("--api-url", type=str, default="http://localhost:8081", help="Base URL for the API.")
    parser.add_argument("--batch-size", type=int, default=5, help="Number of files to upload per request.")
    
    args = parser.parse_args()
    
    # Allow relative path from script dir if not absolute
    if not os.path.isabs(args.path) and not os.path.exists(args.path):
        # Try relative to project root
        proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        alt_path = os.path.join(proj_root, "apps", "resume-analyzer", args.path)
        if os.path.exists(alt_path):
            args.path = alt_path
            
    load_dataset(args.path, args.api_url, args.batch_size)
