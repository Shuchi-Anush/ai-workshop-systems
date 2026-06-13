# AI Resume Intelligence Workshop - Operations Manual

## 1. Hardware Requirements
- **Minimum RAM:** 8GB (16GB recommended for parallel Ollama execution)
- **Minimum Disk:** 5GB free space (for models and vector databases)
- **CPU:** Multi-core modern CPU (Intel i5/i7, AMD Ryzen, Apple Silicon)
- **OS:** Windows 10/11 (via PowerShell/WSL), macOS 13+, Linux (Ubuntu 22.04+)

## 2. Environment Bootstrap
To validate your environment, run:
```bash
uv run python scripts/bootstrap_workshop.py
```
This single command ensures Python, uv, Ollama, Models, Database permissions, and API health are all verified.

## 3. Operational Limits & Expectations
- **Startup Latency:** Model loading (phi3, nomic) may take up to 10-15 seconds on the first request.
- **Retrieval Latency:** 
  - Dense (ChromaDB): ~40ms
  - Sparse (BM25): ~30ms
  - Hybrid RRF: ~35ms
- **Concurrency Limit:** The `uvicorn` backend is limited to `--workers 1` to prevent local Ollama context exhaustion on 8GB machines.

## 4. Troubleshooting & Recovery
### Ollama Fails to Start or Bind Port
- **Windows:** Ensure Ollama is not blocked by Windows Defender. Stop any other services on `11434`.
- **MacOS:** Restart the Ollama background service via the menubar.
- **Linux/WSL:** Run `systemctl restart ollama`.

### Database Corruption / Missing Indexes
If you encounter `sqlite3.DatabaseError` or missing BM25 results, run the repair utility:
```bash
uv run python scripts/repair_environment.py
```
This utility resets the Vector Store and forces a complete BM25 re-index from the benchmark_ready dataset.

## 5. Benchmark Baselines
Running `uv run python tests/retrieval_benchmarks/run_evaluations.py` should approximate:
- **MRR (Hybrid):** 0.50
- **R@3 (Hybrid):** 0.23
- **Adversarial Leaks:** < 4
