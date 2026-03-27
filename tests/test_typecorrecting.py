from dataclasses import dataclass

import pytest

from coerce_type import TypeCorrecting


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
    class PassThrough(TypeCorrecting(pass_through={"string_truthiness": string_truthiness})):
        bt: bool
    coerced = PassThrough.from_dict(args)
    assert coerced.bt == result

