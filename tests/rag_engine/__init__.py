__all__ = ["RagEngine"]

def __getattr__(name):
    if name == "RagEngine":
        from .rag_engine import RagEngine
        return RagEngine
    raise AttributeError(name)