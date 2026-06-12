from ai_contracts.providers.registry import DependencyRegistry

# Global container instance for the application lifecycle.
# In a full FastAPI app, this might be attached to app.state.
global_container = DependencyRegistry()

def get_container() -> DependencyRegistry:
    return global_container
