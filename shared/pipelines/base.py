import time
from typing import Callable, Any, TypeVar

T = TypeVar('T')

class PipelineObservabilityMixin:
    """
    Base class providing lightweight observability and tracing hooks.
    """
    
    def _trace_execution(self, stage_name: str, trace_id: str, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Wraps function execution to log timing and trace propagation.
        In production, this would integrate with OpenTelemetry.
        """
        start_time = time.time()
        # Simulated trace start hook
        # print(f"[TRACE:{trace_id}] Starting {stage_name}")
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000
        # Simulated trace end hook
        # print(f"[TRACE:{trace_id}] Completed {stage_name} in {elapsed_ms:.2f}ms")
        
        return result
