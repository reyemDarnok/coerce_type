import inspect
from abc import ABC, abstractmethod
from dataclasses import fields
from typing import Type, Self

from coerce_type import coerce


class TypeCorrectingType:
    def __post_init__(self) -> None:
        raise NotImplementedError("Call TypeCorrecting instead of using this as a base class")

    @classmethod
    def from_dict(cls, env: dict) -> Self:
        raise NotImplementedError("Call TypeCorrecting instead of using this as a base class")


# noinspection PyPep8Naming
def TypeCorrecting() -> Type[TypeCorrectingType]:
    """Create a parent type for a dataclass that enforces the type annotations on its members"""

    def __post_init__(self) -> None:
        # noinspection PyDataclass,PyTypeChecker
        # making TypeCorrecting a dataclass unnecessarily locks in certain choices
        my_fields = fields(self)
        for my_field in my_fields:
            object.__setattr__(self, my_field.name, coerce(self.__getattribute__(my_field.name), my_field.type))

    # noinspection PyDecorator
    @classmethod
    def from_dict(cls, env: dict):
        return cls(**{k: v for k, v in env.items() if k in inspect.signature(cls).parameters})

    # noinspection PyTypeChecker
    return type("TypeCorrecting", (TypeCorrectingType,), {"__post_init__": __post_init__, "from_dict": from_dict})
