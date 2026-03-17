import sys
from enum import Enum
from types import NoneType, UnionType
from typing import Any, ParamSpec, Type, TypeVar, Union, get_args, get_origin, Literal

T = TypeVar("T")


def coerce(
    obj: Any,
    type_: Type[T] | UnionType,
    *,
    lower_true_strings: tuple[str] = ("true", "t", "1", "yes", "y", "on"),
    str_truthiness: bool = False,
) -> T:
    kwargs = {"lower_true_strings": lower_true_strings, "str_truthiness": str_truthiness}
    origin_type = get_origin(type_)
    if origin_type is not None:
        return coerce_generic(obj, origin_type, get_args(type_), **kwargs)
    if issubclass(type_, Enum):
        return coerce_enum(obj, type_, **kwargs)
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


def coerce_generic(obj: Any, origin_type: ParamSpec, type_args: tuple[Any, ...], **kwargs) -> T:
    get_origin(obj)
    if origin_type == Literal:
        coerced_obj = coerce(obj, type(type_args[0]), **kwargs)  # attempt to match the type of the literal
        if coerced_obj == type_args[0]:
            return type_args[0]
        else:
            raise ValueError(f"Cannot coerce {obj} to Literal {type_args[0]}")
    if origin_type == list:
        member_type = type_args[0]
        return [coerce(member, member_type, **kwargs) for member in obj]
    if origin_type == dict:
        key_type, value_type = type_args
        return {coerce(key, key_type, **kwargs): coerce(value, value_type, **kwargs) for key, value in obj.items()}
    if origin_type in (Union, UnionType):
        return coerce_union(obj, origin_type, type_args, **kwargs)
    raise TypeError(f"Cannot recognize generic type {origin_type}")


def coerce_union(obj: Any, origin_type: ParamSpec, type_args: tuple[Any, ...], **kwargs) -> T:
    # prioritize keeping None as none and not coerce it to something else
    if NoneType in type_args:
        try:
            return coerce(obj, NoneType, **kwargs)
        except ValueError:
            pass
    for type_in_union in type_args:
        try:
            return coerce(obj, type_in_union, **kwargs)
        except ValueError:
            pass
    else:
        raise ValueError(f"Cannot coerce {obj} to {origin_type} with type arguments {type_args}")


E = TypeVar("E", bound=Enum)


def coerce_enum(obj: Any, type_: Type[E], **kwargs) -> E:
    if sys.version_info >= (3, 12):
        if obj in type_:
            return type_(obj)
    else:
        try:
            return type_(obj)
        except ValueError:
            pass
    if obj in type_.__members__.keys():
        return type_[obj]
    raise ValueError(f"Cannot coerce {obj} to member of Enum {type_}")
