import inspect
import sys
from dataclasses import fields
from typing import Type, TypeAlias

if sys.version_info >= (3, 11):
    from typing import Self
else:
    Self: TypeAlias = "TypeCorrectingType"

from coerce_type import coerce


class TypeCorrectingType:
    def __post_init__(self) -> None:
        raise NotImplementedError("Call TypeCorrecting instead of using this as a base class")

    @classmethod
    def from_dict(cls, env: dict) -> Self:
        raise NotImplementedError("Call TypeCorrecting instead of using this as a base class")


# noinspection PyPep8Naming
def TypeCorrecting(exclude_fields=None, **kwargs) -> Type[TypeCorrectingType]:
    """
    Create a parent type for a dataclass that enforces the type annotations on its members
    :param exclude_fields: Ignore these fields when coercing. Defaults to []
    :param kwargs: Passed through to coerce as kwargs"""

    if exclude_fields is None:
        exclude_fields = []

    def __post_init__(self) -> None:
        # noinspection PyDataclass,PyTypeChecker
        # making TypeCorrecting a dataclass unnecessarily locks in certain choices
        my_fields = fields(self)
        for my_field in my_fields:
            if my_field.name in exclude_fields:
                continue
            object.__setattr__(
                self, my_field.name, coerce(self.__getattribute__(my_field.name), my_field.type, **kwargs)
            )

    # noinspection PyDecorator
    @classmethod
    def from_dict(cls, env: dict):
        return cls(**{k: v for k, v in env.items() if k in inspect.signature(cls).parameters})

    # noinspection PyTypeChecker
    return type("TypeCorrecting", (TypeCorrectingType,), {"__post_init__": __post_init__, "from_dict": from_dict})
