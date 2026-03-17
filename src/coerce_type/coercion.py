from os import GenericAlias
from typing import Any, Type, TypeVar, get_origin, get_args

T = TypeVar("T")


def coerce(
    obj: Any,
    typ: Type[T],
    *,
    lower_true_strings: tuple[str] = ("true", "t", "1", "yes", "y", "on"),
    str_truthiness: bool = False,
) -> T:
    kwargs = {"lower_true_strings": lower_true_strings, "str_truthiness": str_truthiness}
    if get_origin(typ) == list:
        member_type = get_args(typ)[0]
        return [coerce(member, member_type, **kwargs) for member in obj]
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
