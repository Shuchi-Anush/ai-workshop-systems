import requests

# 1. Ingest
ingest_url = "http://localhost:8080/ingest"
with open("apps/resume-analyzer/dummy_resume.pdf", "rb") as f:
    files = {"file": f}
    data = {"candidate_id": "john_doe"}
    resp_ingest = requests.post(ingest_url, files=files, data=data)
    print("Ingest:", resp_ingest.json())

# 2. Evaluate
eval_url = "http://localhost:8080/evaluate"
payload = {
    "job_description": "Looking for a Software Engineer with Python and FastAPI experience.",
    "top_k": 5
}
response = requests.post(eval_url, json=payload)
print("Evaluate:", response.json())
