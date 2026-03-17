import collections
import inspect
import sys
from enum import Enum
from functools import partial
from types import NoneType, UnionType
from typing import Any, Callable, ClassVar, Generic, Literal, ParamSpec, Type, TypeVar, Union, get_args, get_origin

T = TypeVar("T")


def coerce(
    obj: Any,
    type_: Type[T] | UnionType,
    *,
    echo_on_failure: bool = False,
    lower_true_strings: tuple[str] = ("true", "t", "1", "yes", "y", "on"),
    str_truthiness: bool = False,
) -> T:
    kwargs = {
        "lower_true_strings": lower_true_strings,
        "str_truthiness": str_truthiness,
        "echo_on_failure": echo_on_failure,
    }
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
    # noinspection PyBroadException
    try:
        return coerce_constructor(obj, type_, **kwargs)
    except Exception:
        if echo_on_failure:
            return obj
        else:
            raise ValueError(f"Cannot coerce {obj} to {type_}")


def coerce_generic(obj: Any, origin_type: ParamSpec, type_args: tuple[Any, ...], **kwargs) -> T:
    if origin_type == Generic:
        return obj
    if origin_type in (Callable, collections.abc.Callable):
        return coerce_callable(obj, type_args, **kwargs)
    if origin_type == Literal:
        return coerce_literal(obj, type_args, **kwargs)
    if origin_type == ClassVar:
        return coerce(obj, type_args[0], **kwargs)
    if origin_type == list:
        member_type = type_args[0]
        return [coerce(member, member_type, **kwargs) for member in obj]
    if origin_type == dict:
        key_type, value_type = type_args
        return {coerce(key, key_type, **kwargs): coerce(value, value_type, **kwargs) for key, value in obj.items()}
    if origin_type in (Union, UnionType):
        return coerce_union(obj, origin_type, type_args, **kwargs)
    if kwargs["echo_on_failure"]:
        return obj
    else:
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
        if kwargs["echo_on_failure"]:
            return obj
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
    if kwargs["echo_on_failure"]:
        return obj
    else:
        raise ValueError(f"Cannot coerce {obj} to member of Enum {type_}")


def coerce_literal(obj: Any, literals: tuple[Any, ...], **kwargs) -> Any:
    try:
        return literals[literals.index(obj)]
    except ValueError:
        pass
    for literal in literals:
        try:
            coerced_obj = coerce(obj, type(literal), **kwargs)  # attempt to match the type of the literal
            if coerced_obj == literal:
                return literal
        except ValueError:
            pass  # reachable when a literal does not compare equal to an item in the list, but can be coerced to it
    else:
        if kwargs["echo_on_failure"]:
            return obj
        else:
            raise ValueError(f"Cannot coerce {obj} to any of Literal {literals}")


def coerce_callable(obj: Any, type_args: tuple[Any, ...], **kwargs):
    current_signature = inspect.signature(obj)

    def echo(a: T) -> T:
        return a

    number_mandatory = sum(param.default is inspect.Parameter.empty for param in current_signature.parameters.values())
    number_total = len(current_signature.parameters)
    if not number_mandatory <= len(type_args) <= number_total:
        if kwargs["echo_on_failure"]:
            return obj
        else:
            raise ValueError(f"Cannot coerce {obj} to of Callable with args {type_args}")
    coercer_args = []
    coercer_kwargs = {}
    for index, (parameter_name, parameter) in enumerate(current_signature.parameters.items()):
        if parameter.annotation is inspect.Parameter.empty or issubclass(parameter.annotation, type_args[0][index]):
            coercer = echo
        else:
            coercer = partial(coerce, type_=parameter.annotation, **kwargs)
        if parameter.POSITIONAL_ONLY or parameter.POSITIONAL_OR_KEYWORD:
            coercer_args.append(coercer)
        else:
            coercer_kwargs[parameter_name] = coercer
    if current_signature.return_annotation is inspect.Signature.empty or not issubclass(
        current_signature.return_annotation, type_args[1]
    ):
        return_coercer = partial(coerce, type_=type_args[1], **kwargs)
    else:
        return_coercer = echo

    def coercion_wrapper(*args, **local_kwargs):
        res = obj(
            *[c(arg) for c, arg in zip(coercer_args, args)],
            **{key: c(val) for c, (key, val) in zip(coercer_kwargs, local_kwargs)},
        )
        return return_coercer(res)

    return coercion_wrapper


# noinspection PyBroadException
# the woe of libraries calling user-code: Having no idea what kind of exceptions can be thrown
def coerce_constructor(obj: Any, type_: Type[T], **kwargs) -> T:
    if isinstance(obj, dict):
        # noinspection PyBroadException

        try:
            return type_(**obj)
        except Exception:
            pass
    if isinstance(obj, list):
        try:
            return type_(*obj)
        except Exception:
            pass
    else:
        try:
            return type_(obj)
        except Exception:
            pass
    if kwargs["echo_on_failure"]:
        return obj
    else:
        raise ValueError(f"Cannot coerce {obj} to type {type_}")