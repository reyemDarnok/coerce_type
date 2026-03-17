from dataclasses import dataclass

import pytest

from coerce_type import TypeCorrecting


@dataclass
class Simple(TypeCorrecting()):
    a: int
    b: str

@pytest.mark.parametrize(
    "args, a, b", [
        ({"a": 1, "b": "text"}, 1, "text"),
        ({"a": "4", "b": True}, 4, "True"),
    ]
)
def test_simple(args, a, b,):
    coerced = Simple(**args)
    assert coerced.a == a
    assert coerced.b == b