from dataclasses import dataclass

import pytest

from coerce_type import TypeCorrecting, TypeCorrectingType


@dataclass
class Simple(TypeCorrecting()):
    a: int
    b: str


@pytest.mark.parametrize(
    "args, a, b",
    [
        ({"a": 1, "b": "text"}, 1, "text"),
        ({"a": "4", "b": True}, 4, "True"),
    ],
)
def test_simple(
    args,
    a,
    b,
):
    coerced = Simple(**args)
    assert coerced.a == a
    assert coerced.b == b


@pytest.mark.parametrize(
    "args, a, b",
    [
        ({"a": 1, "b": "text"}, 1, "text"),
        ({"a": "4", "b": True, "c": "ignore me"}, 4, "True"),
    ],
)
def test_from_dict(
    args,
    a,
    b,
):
    coerced = Simple.from_dict(args)
    assert coerced.a == a
    assert coerced.b == b


@pytest.mark.parametrize(
    "args, string_truthiness, result",
    [
        ({"bt": "False"}, True, True),
        ({"bt": "False"}, False, False),
    ],
)
def test_pass_through(args, string_truthiness, result):
    @dataclass()
    class PassThrough(TypeCorrecting(str_truthiness=string_truthiness)):
        bt: bool

    coerced = PassThrough.from_dict(args)
    assert coerced.bt == result


@pytest.mark.parametrize(
    "args, exclude, a, b",
    [
        ({"a": "1", "b": "2"}, ["b"], 1, "2"),
        ({"a": "1", "b": "2"}, ["a"], "1", 2),
        ({"a": "1", "b": "2"}, ["a", "b"], "1", "2"),
        ({"a": "1", "b": "2"}, [], 1, 2),
    ],
)
def test_exclusion(args, exclude, a, b):
    @dataclass()
    class Exclude(TypeCorrecting(exclude_fields=exclude)):
        a: int
        b: int

    coerced = Exclude.from_dict(args)
    assert coerced.a == a
    assert coerced.b == b


def test_superclass_complain_init():
    with pytest.raises(NotImplementedError):

        @dataclass
        class TestClass(TypeCorrectingType):
            pass

        TestClass()


def test_superclass_complain_from_dict():
    with pytest.raises(NotImplementedError):

        @dataclass
        class TestClass(TypeCorrectingType):
            pass

        TestClass.from_dict({})
