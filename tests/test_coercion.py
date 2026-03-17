import pytest

import coerce_type


@pytest.mark.parametrize(
    "obj, typ, result",
    [
        (5, int, 5),
        (0.2, float, 0.2),
        ("text", str, "text"),
    ],
)
def test_coerce(obj, typ, result) -> None:
    assert coerce_type.coerce(obj, typ) == result


def test_coerce_fail() -> None:
    with pytest.raises(ValueError):
        coerce_type.coerce("some text", int)
