from typing import Dict, Type, Any, Callable
from shared.interfaces.vectordb import IVectorDB
from shared.interfaces.storage import IMetadataStore

class DependencyRegistry:
    """
    Lightweight dependency registry.
    Prevents hardcoded implementation imports in the service layer.
    """
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        
    def register_singleton(self, interface: Type, implementation: Any) -> None:
        self._services[interface] = implementation
        
    def register_factory(self, interface: Type, factory: Callable[[], Any]) -> None:
        self._factories[interface] = factory
        
    def resolve(self, interface: Type) -> Any:
        if interface in self._services:
            return self._services[interface]
        if interface in self._factories:
            return self._factories[interface]()
            
        raise ValueError(f"No registered implementation found for {interface.__name__}")
        
    def clear(self) -> None:
        self._services.clear()
        self._factories.clear()
