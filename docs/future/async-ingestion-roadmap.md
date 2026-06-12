# Async Ingestion Roadmap

Parsing PDFs and generating embeddings are CPU/GPU bound tasks that will timeout standard HTTP requests.

**Plan**:
1. Introduce Celery + Redis as a task queue.
2. Refactor `IIngestionService` to enqueue tasks rather than process synchronously.
3. API endpoints will return a `task_id` and a `202 Accepted` status.
4. Implement a polling endpoint or webhook callback to notify the client when a candidate's resume has been fully indexed.
