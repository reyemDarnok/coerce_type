from typing import Any, Type, TypeVar

T = TypeVar("T")


def coerce(
    obj: Any,
    typ: Type[T],
    *,
    lower_true_strings: tuple[str] = ("true", "t", "1", "yes", "y", "on"),
    str_truthiness: bool = False,
) -> T:
    if isinstance(obj, typ):
        return obj
    if typ in (int, float, str):
        return typ(obj)
    if typ is bool:
        if isinstance(obj, str) and not str_truthiness:
            return obj.lower() in lower_true_strings
        else:
            return bool(obj)
    raise ValueError(f"Cannot coerce {obj} to {typ}")
