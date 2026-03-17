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

def test_non_str_bool_conversion() -> None:
    assert coerce_type.coerce([1], bool) == True
    assert coerce_type.coerce([], bool) == False

def test_str_truthiness() -> None:
    assert coerce_type.coerce("False", bool, str_truthiness=True) == True
    assert coerce_type.coerce("", bool, str_truthiness=True) == False

def test_custom_str_truthiness() -> None:
    assert coerce_type.coerce("Really", bool, lower_true_strings=("really",)) == True
    assert coerce_type.coerce("Nah", bool, lower_true_strings=("really",)) == False
    assert coerce_type.coerce("True", bool, lower_true_strings=("really",)) == False

def test_custom_str_truthiness_is_overridden() -> None:
    assert coerce_type.coerce("Really", bool, str_truthiness=True, lower_true_strings=("really",)) == True
    assert coerce_type.coerce("Nah", bool, str_truthiness=True, lower_true_strings=("really",)) == True
    assert coerce_type.coerce("a", bool, str_truthiness=True, lower_true_strings=("really",)) == True
    assert coerce_type.coerce("", bool, str_truthiness=True, lower_true_strings=("really",)) == False



def test_fail_builtin() -> None:
    with pytest.raises(ValueError):
        coerce_type.coerce("some text", int)

def test_fail_non_builtin() -> None:
    class CustomClass:
        pass
    with pytest.raises(ValueError):
        coerce_type.coerce("some text", CustomClass)