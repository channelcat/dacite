from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, List, Union

import pytest

from dacite import from_dict, Config, ForwardReferenceError, UnexpectedDataError


def test_from_dict_with_type_hooks():
    @dataclass
    class X:
        s: str

    result = from_dict(X, {"s": "TEST"}, Config(type_hooks={str: str.lower}))

    assert result == X(s="test")


def test_from_dict_with_type_hooks_and_optional():
    @dataclass
    class X:
        s: Optional[str]

    result = from_dict(X, {"s": "TEST"}, Config(type_hooks={str: str.lower}))

    assert result == X(s="test")


def test_from_dict_with_type_hooks_and_union():
    @dataclass
    class X:
        s: Union[str, int]

    result = from_dict(X, {"s": "TEST"}, Config(type_hooks={str: str.lower}))

    assert result == X(s="test")


def test_from_dict_with_generic_type_hooks():
    @dataclass
    class X:
        s: str

    result = from_dict(X, {"s": "TEST"}, Config(type_hooks={Any: str.lower}))

    assert result == X(s="test")


def test_from_dict_with_generic_list_type_hooks():
    @dataclass
    class X:
        l: List[int]

    result = from_dict(X, {"l": [3,1,2]}, Config(type_hooks={List: sorted}))

    assert result == X(l=[1,2,3])


def test_from_dict_with_generic_dict_type_hooks():
    @dataclass
    class X:
        d: Dict[str, int]
    
    def add_b(value):
        value["b"] = 2
        return value

    result = from_dict(X, {"d": {"a": 1}}, Config(type_hooks={Dict: add_b}))

    assert result == X(d={"a": 1, "b": 2})


def test_from_dict_with_cast():
    @dataclass
    class X:
        s: str

    result = from_dict(X, {"s": 1}, Config(cast=[str]))

    assert result == X(s="1")


def test_from_dict_with_base_class_cast():
    class E(Enum):
        A = "a"

    @dataclass
    class X:
        e: E

    result = from_dict(X, {"e": "a"}, Config(cast=[Enum]))

    assert result == X(e=E.A)


def test_from_dict_with_base_class_cast_and_optional():
    class E(Enum):
        A = "a"

    @dataclass
    class X:
        e: Optional[E]

    result = from_dict(X, {"e": "a"}, Config(cast=[Enum]))

    assert result == X(e=E.A)


def test_from_dict_with_cast_and_generic_collection():
    @dataclass
    class X:
        s: List[int]

    result = from_dict(X, {"s": (1,)}, Config(cast=[List]))

    assert result == X(s=[1])


def test_from_dict_with_type_hooks_and_generic_sequence():
    @dataclass
    class X:
        c: List[str]

    result = from_dict(X, {"c": ["TEST"]}, config=Config(type_hooks={str: str.lower}))

    assert result == X(c=["test"])


def test_from_dict_with_forward_reference():
    @dataclass
    class X:
        y: "Y"

    @dataclass
    class Y:
        s: str

    data = from_dict(X, {"y": {"s": "text"}}, Config(forward_references={"Y": Y}))
    assert data == X(Y("text"))


def test_from_dict_with_missing_forward_reference():
    @dataclass
    class X:
        y: "Y"

    @dataclass
    class Y:
        s: str

    with pytest.raises(ForwardReferenceError) as exception_info:
        from_dict(X, {"y": {"s": "text"}})

    assert str(exception_info.value) == "can not resolve forward reference: name 'Y' is not defined"


def test_form_dict_with_disabled_type_checking():
    @dataclass
    class X:
        i: int

    result = from_dict(X, {"i": "test"}, config=Config(check_types=False))

    # noinspection PyTypeChecker
    assert result == X(i="test")


def test_form_dict_with_disabled_type_checking_and_union():
    @dataclass
    class X:
        i: Union[int, float]

    result = from_dict(X, {"i": "test"}, config=Config(check_types=False))

    # noinspection PyTypeChecker
    assert result == X(i="test")


def test_from_dict_with_strict():
    @dataclass
    class X:
        s: str

    with pytest.raises(UnexpectedDataError) as exception_info:
        from_dict(X, {"s": "test", "i": 1}, Config(strict=True))

    assert str(exception_info.value) == 'can not match "i" to any data class field'
