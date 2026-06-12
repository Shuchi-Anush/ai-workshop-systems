# Repository Conventions

* **Typing**: Strict type hints required for all Python code.
* **Validation**: Pydantic models required for all data boundaries.
* **Dependencies**: Managed via standard `requirements.txt` with locked versions. `shared/` dependencies must be kept minimal.
* **Testing**: `pytest` mandatory. Unit tests must use mock VectorDB and Embedders to run offline and deterministically.
