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
def test_coerce_default_args(obj, typ, result) -> None:
    assert coerce_type.coerce(obj, typ) == result

def test_coerce_fail() -> None:
    with pytest.raises(ValueError):
        coerce_type.coerce("some text", int)
