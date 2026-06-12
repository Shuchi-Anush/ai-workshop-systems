from shared.interfaces.vectordb import IVectorDB
from shared.interfaces.storage import IMetadataStore
from shared.mocks.mock_vectordb import MockVectorDB
from shared.mocks.mock_metadata_store import MockMetadataStore
from .container import get_container

def configure_mock_infrastructure() -> None:
    """
    Wires the container with mock implementations.
    To be used during test initialization and offline architecture stabilization.
    """
    container = get_container()
    
    # Register singletons to preserve state across service calls during testing
    container.register_singleton(IVectorDB, MockVectorDB())
    container.register_singleton(IMetadataStore, MockMetadataStore())
