from types import UnionType, NoneType
from typing import Any, Type, TypeVar, get_args, get_origin, Union

T = TypeVar("T")


def coerce(
    obj: Any,
    type_: Type[T] | UnionType,
    *,
    lower_true_strings: tuple[str] = ("true", "t", "1", "yes", "y", "on"),
    str_truthiness: bool = False,
) -> T:
    kwargs = {"lower_true_strings": lower_true_strings, "str_truthiness": str_truthiness}
    if get_origin(type_) == list:
        member_type = get_args(type_)[0]
        return [coerce(member, member_type, **kwargs) for member in obj]
    if get_origin(type_) == dict:
        key_type, value_type = get_args(type_)
        return {coerce(key, key_type, **kwargs): coerce(value, value_type, **kwargs) for key, value in obj.items()}
    if get_origin(type_) == Union:
        # prioritize keeping None as none and not coerce it to something else
        if NoneType in get_args(type_):
            try:
                return coerce(obj, NoneType, **kwargs)
            except ValueError:
                pass
        for type_in_union in get_args(type_):
            try:
                return coerce(obj, type_in_union, **kwargs)
            except ValueError:
                pass
        else:
            raise ValueError(f"Cannot coerce {obj} to {type_}")
    if isinstance(obj, type_):
        return obj
    if type_ in (int, float, str):
        return type_(obj)
    if type_ is bool:
        if isinstance(obj, str) and not str_truthiness:
            return obj.lower() in lower_true_strings
        else:
            return bool(obj)
    raise ValueError(f"Cannot coerce {obj} to {type_}")
