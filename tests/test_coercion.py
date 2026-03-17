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
    assert coerce_type.coerce([1], bool)
    assert not coerce_type.coerce([], bool)


def test_str_truthiness() -> None:
    assert coerce_type.coerce("False", bool, str_truthiness=True)
    assert not coerce_type.coerce("", bool, str_truthiness=True)


def test_custom_str_truthiness() -> None:
    assert coerce_type.coerce("Really", bool, lower_true_strings=("really",))
    assert not coerce_type.coerce("Nah", bool, lower_true_strings=("really",))
    assert not coerce_type.coerce("True", bool, lower_true_strings=("really",))


def test_custom_str_truthiness_is_overridden() -> None:
    assert coerce_type.coerce("Really", bool, str_truthiness=True, lower_true_strings=("really",))
    assert coerce_type.coerce("Nah", bool, str_truthiness=True, lower_true_strings=("really",))
    assert coerce_type.coerce("a", bool, str_truthiness=True, lower_true_strings=("really",))
    assert not coerce_type.coerce("", bool, str_truthiness=True, lower_true_strings=("really",))


def test_fail_builtin() -> None:
    with pytest.raises(ValueError):
        coerce_type.coerce("some text", int)


def test_fail_non_builtin() -> None:
    class CustomClass:
        pass

    with pytest.raises(ValueError):
        coerce_type.coerce("some text", CustomClass)

def test_typing_lists() -> None:
    assert coerce_type.coerce([1,2,3], list[str]) == ["1", "2", "3"]

def test_typing_list_kwargs() -> None:
    assert coerce_type.coerce(["Really",0,1], list[bool], lower_true_strings=("really",)) == [True, False, True]

def test_typing_dicts() -> None:
    assert coerce_type.coerce({"0.2": "1", "0.5": "2"}, dict[float, int]) == {0.2: 1, 0.5: 2}

def test_typing_dicts_kwargs() -> None:
    assert coerce_type.coerce({"0.2": "1", "0.5": "2"}, dict[float, bool],
                              lower_true_strings=("2",)) == {0.2: False, 0.5: True}
