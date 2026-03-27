import collections
import datetime
import inspect
import sys
from datetime import timezone
from enum import Enum
from functools import partial
from types import NoneType, UnionType
from typing import Any, Callable, ClassVar, Generic, Literal, ParamSpec, Type, TypeVar, Union, get_args, get_origin

T = TypeVar("T")
S = TypeVar("S")


def coerce(
    obj: Any,
    type_: Type[T] | UnionType,
    *,
    echo_on_failure: bool = False,
    lower_true_strings: tuple[str] = ("true", "t", "1", "yes", "y", "on"),
    str_truthiness: bool = False,
    custom_type_converters: dict[Type[T], dict[Type[S], Callable[[S], T]]] = None,
) -> T:
    """Coerce a value to a given type. Complex nested types are supported.
    :param obj: The value to coerce.
    :param type_: The target type.
    :param echo_on_failure: When type coercion fails return input obj instead of ValueError.
    :param lower_true_strings: A list of lowercase strings that are treated as True for boolean conversion.
    :param str_truthiness: If True, use python truthiness for strings instead of lower_true_strings.
    :param custom_type_converters: Custom type converters {str: {int: nice_int_formatter }}
                                    would call nice_int_formatter when coercing an int to a str.
    :raises ValueError: When type coercion fails and echo_on_failure is False.
    """
    type_converters = {
        datetime.datetime: {
            float: partial(datetime.datetime.fromtimestamp, tz=timezone.utc),
            str: datetime.datetime.fromisoformat,
        },
        datetime.date: {float: datetime.date.fromtimestamp, str: datetime.date.fromisoformat},
    }
    if custom_type_converters:
        type_converters.update(custom_type_converters)
    kwargs = {
        "lower_true_strings": lower_true_strings,
        "str_truthiness": str_truthiness,
        "echo_on_failure": echo_on_failure,
        "custom_type_converters": type_converters,
    }
    if type_ in type_converters:
        return coerce_custom(obj, type_, **kwargs)
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
    except Exception as e:
        if echo_on_failure:
            return obj
        else:
            raise ValueError(f"Cannot coerce {obj} to {type_}") from e


def coerce_generic(obj: Any, origin_type: ParamSpec, type_args: tuple[Any, ...], **kwargs) -> T:
    """Coerce a value to match a given generic type. Prefer coerce if you are unsure.
    :param obj: The value to coerce.
    :param origin_type: The target Generic Type. I.e. list for list[int]
    :param type_args: The arguments to the generic type. I.e. (int,) for list[int]
    :param kwargs: See coerce for details
    :raises ValueError: When type coercion fails and echo_on_failure is False."""
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
        return coerce_union(obj, type_args, **kwargs)
    if origin_type == tuple:
        return coerce_tuple(obj, type_args, **kwargs)
    if kwargs["echo_on_failure"]:
        return obj
    else:
        raise TypeError(f"Cannot recognize generic type {origin_type}")


def coerce_tuple(obj: Any, type_args: tuple[Any, ...], **kwargs) -> T:
    """Coerce a value to a tuple of a given type.
    :param obj: The value to coerce.
    :param type_args: The member types of the tuple
    :param kwargs: See coerce for details
    :raises ValueError: When type coercion fails and echo_on_failure is False."""
    result_data = []
    if type_args[-1] == ...:
        type_args = type_args[:-1] + (type_args[-2],) * (len(obj) - len(type_args) + 1)
    if len(obj) != len(type_args):
        if kwargs["echo_on_failure"]:
            return obj
        else:
            raise ValueError(f"Cannot coerce iterable with length {len(obj)} to tuple of length {len(type_args)}")
    for member, type_ in zip(obj, type_args):
        result_data.append(coerce(member, type_, **kwargs))

    return tuple(result_data)


def coerce_union(obj: Any, type_args: tuple[Any, ...], **kwargs) -> T:
    """Coerce a value to a member of a union of types.
    :param obj: The value to coerce.
    :param type_args: The member types of the union
    :param kwargs: See coerce for details
    :raises ValueError: When type coercion fails and echo_on_failure is False."""
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
            raise ValueError(f"Cannot coerce {obj} to Union with members {type_args}")


E = TypeVar("E", bound=Enum)


def coerce_enum(obj: Any, type_: Type[E], **kwargs) -> E:
    """Coerce a value to a member of an enum. Will attempt to match both by name and value of the enum member
    :param obj: The value to coerce.
    :param type_: The target Enum
    :param kwargs: See coerce for details
    :raises ValueError: When type coercion fails and echo_on_failure is False.
    """
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
    """Coerce a value to a literal type. Will type coerce a value to match the types of the literal,
    trying first for exact matches and then attempts to type coerce in the order of the literal.
    :param obj: The value to coerce.
    :param literals: The target literals
    :param kwargs: See coerce for details
    :raises ValueError: When type coercion fails and echo_on_failure is False.
    """
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
    """Coerce a callable to a given type signature.
    Will attempt to type coerce each argument from type_args to the signature of obj
    and the return value of obj to the return value in type_args
    :param obj: The callable to coerce.
    :param type_args: The target signature
    :param kwargs: See coerce for details
    :returns: A wrapper around the callable. This wrapper may throw a ValueError
              when the coercion of arguments of return values fails
    """
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
    """Uses a types constructor to coerce a value to it. Attempts both dict and
    list spreads before calling the constructor with a single argument.
    :param obj: The value to coerce.
    :param type_: The type to coerce to.
    :param kwargs: See coerce for details
    :raises ValueError: When type coercion fails and echo_on_failure is False."""
    if isinstance(obj, dict):
        # noinspection PyBroadException

        try:
            return type_(**obj)
        except Exception:
            pass
    elif isinstance(obj, list):
        try:
            return type_(*obj)
        except Exception:
            pass
    else:
        try:
            return type_(obj)
        except Exception as e:
            if kwargs["echo_on_failure"]:
                return obj
            else:
                raise ValueError(f"Cannot coerce {obj} to type {type_}") from e


C = TypeVar("C")


def coerce_custom(obj: Any, type_: Type[C], **kwargs) -> C:
    """Coerce a value using custom conversion functions.
    :param obj: The value to coerce.
    :param type_: The type to coerce to.
    :param kwargs: See coerce for details
    :raises ValueError: When type coercion fails and echo_on_failure is False."""
    converters: dict[Type[C], dict[Type[S], Callable[[S], C]]] = kwargs["custom_type_converters"]
    type_converters = converters[type_]
    if type(obj) in type_converters:
        return type_converters[type(obj)](obj)
    else:
        for source_type, converter in type_converters.items():
            try:
                source = coerce(obj, source_type, **kwargs)
            except ValueError:
                break
            return converter(source)
        else:
            if kwargs["echo_on_failure"]:
                return obj
            else:
                raise ValueError(
                    f"No custom coercion possible for type {type_}. "
                    f"Coercion to any of the following types not possible: {type_converters.keys()}"
                )
