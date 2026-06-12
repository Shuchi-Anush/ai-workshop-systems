# Run script for Task 01 Resume RAG
echo "Starting Task 01 Resume RAG Service..."
uvicorn task_01_resume_rag.src.api.main:app --reload
