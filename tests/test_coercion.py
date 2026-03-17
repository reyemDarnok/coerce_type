import datetime
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Generic, Literal

import pytest

import coerce_type


@pytest.mark.parametrize(
    "obj, typ, result",
    [
        # no-op coercions
        (5, int, 5),
        (0.2, float, 0.2),
        ("text", str, "text"),
        (True, bool, True),
        # coercions of build in types
        (1.0, int, 1),
        ("10", int, 10),
        ("0.2", float, 0.2),
        ("True", bool, True),
        ("False", bool, False),
        (5, str, "5"),
        (0.2, str, "0.2"),
    ],
)
def test_default_args(obj, typ, result) -> None:
    assert coerce_type.coerce(obj, typ) == result


@pytest.mark.parametrize("obj, result", [([1], True), ([], False)])
def test_non_str_bool_conversion(obj, result) -> None:
    assert coerce_type.coerce(obj, bool) == result


@pytest.mark.parametrize("obj, result", [("False", True), ("", False)])
def test_str_truthiness(obj, result) -> None:
    assert coerce_type.coerce(obj, bool, str_truthiness=True) == result


@pytest.mark.parametrize(
    "obj, result",
    [
        ("Really", True),
        ("Nah", False),
        ("True", False),
    ],
)
def test_custom_str_truthiness(obj, result) -> None:
    assert coerce_type.coerce(obj, bool, lower_true_strings=("really",)) == result


@pytest.mark.parametrize(
    "obj, result",
    [
        ("Really", True),
        ("Nah", True),
        ("a", True),
        ("", False),
    ],
)
def test_custom_str_truthiness_is_overridden(obj, result) -> None:
    assert coerce_type.coerce(obj, bool, str_truthiness=True, lower_true_strings=("really",)) == result


def test_fail_builtin() -> None:
    with pytest.raises(ValueError):
        coerce_type.coerce("some text", int)


def test_fail_non_builtin() -> None:
    class CustomClass:
        pass

    with pytest.raises(ValueError):
        coerce_type.coerce("some text", CustomClass)


def test_typing_lists() -> None:
    assert coerce_type.coerce([1, 2, 3], list[str]) == ["1", "2", "3"]


def test_typing_list_kwargs() -> None:
    assert coerce_type.coerce(["Really", 0, 1], list[bool], lower_true_strings=("really",)) == [True, False, True]


def test_typing_dicts() -> None:
    assert coerce_type.coerce({"0.2": "1", "0.5": "2"}, dict[float, int]) == {0.2: 1, 0.5: 2}


def test_typing_dicts_kwargs() -> None:
    assert coerce_type.coerce({"0.2": "1", "0.5": "2"}, dict[float, bool], lower_true_strings=("2",)) == {
        0.2: False,
        0.5: True,
    }


@pytest.mark.parametrize(
    "value, type_, result",
    [
        ("True", int | bool, True),
        ("4", int | bool, 4),
    ],
)
def test_union_of_existing(value, type_, result) -> None:
    assert coerce_type.coerce(value, type_) == result


def test_union_fail() -> None:
    with pytest.raises(ValueError):
        coerce_type.coerce("some text", int | float)


def test_optional():
    assert coerce_type.coerce(None, int | None) is None


def test_optional_fail() -> None:
    with pytest.raises(ValueError):
        assert coerce_type.coerce("some text", int | None)


class SampleEnum(Enum):
    ONE = 1
    TWO = 2
    THREE = 3


def test_enum_by_value():
    assert coerce_type.coerce(1, SampleEnum) == SampleEnum.ONE


def test_enum_by_name():
    assert coerce_type.coerce("ONE", SampleEnum) == SampleEnum.ONE


def test_enum_fail() -> None:
    with pytest.raises(ValueError):
        coerce_type.coerce("some text", SampleEnum)


def test_literal() -> None:
    assert coerce_type.coerce("42", Literal[42]) == 42


def test_literal_fail() -> None:
    with pytest.raises(ValueError):
        coerce_type.coerce(49, Literal[42])


def test_multi_val_literal() -> None:
    assert coerce_type.coerce(42, Literal[1, 2, 3, 42]) == 42


def test_multi_type_literal() -> None:
    assert coerce_type.coerce("42", Literal["The Answer", 42]) == 42
    assert coerce_type.coerce("The Answer", Literal[42, "The Answer"]) == "The Answer"


def test_class_var() -> None:
    assert coerce_type.coerce(10, ClassVar[int]) == 10


def test_generic() -> None:
    assert coerce_type.coerce(5, Generic) == 5


def test_callable() -> None:
    def sample_func(a: int, b: int) -> int:
        return a + b

    coerced = coerce_type.coerce(sample_func, Callable[[str, str], str])
    assert coerced("1", "2") == "3"


@dataclass
class DirectConstructor:
    a: int


@dataclass
class MultiConstructor:
    a: int
    b: int


@pytest.mark.parametrize(
    "value, type_, result",
    [
        (5, DirectConstructor, DirectConstructor(5)),
        (
            [
                1,
                2,
            ],
            MultiConstructor,
            MultiConstructor(
                1,
                2,
            ),
        ),
        ({"a": 4, "b": 5}, MultiConstructor, MultiConstructor(a=4, b=5)),
    ],
)
def test_constructor(value, type_, result) -> None:
    assert coerce_type.coerce(value, type_) == result

def test_custom() -> None:
    assert coerce_type.coerce("2001-01-01", datetime.date) == datetime.date(2001, 1, 1)