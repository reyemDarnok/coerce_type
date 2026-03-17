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
