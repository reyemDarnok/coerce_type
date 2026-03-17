from typing import TypeVar, Any, Type

T = TypeVar("T")

def coerce(obj: Any, typ: Type[T]) -> T:
    if isinstance(obj, typ):
        return obj
    raise ValueError(f"Cannot coerce {obj} to {typ}")