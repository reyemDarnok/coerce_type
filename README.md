# coerce_type

coerce_type is a library for the type coercion of values 
to the annotations they have. It can be triggered manually with `coerce`
or be set to happen automatically for a dataclass by having it inherit a `TypeCorrecting` class

## Installation

```shell
pip install coerce_type
```

## Usage
There are two main uses of this library:
The `coerce` function and the `TypeCorrecting` class constructor.

### `coerce`
```pycon
>>> from coerce_type import coerce
>>> target_type = int
>>> value = "1"
>>> coerce(value, target_type)
1
```

### `TypeCorrecting`

```pycon
>>>import datetime from coerce_type import TypeCorrecting, TypeCorrectingType
>>> from dataclasses import dataclass
>>> from datetime import date
>>> @dataclass()
>>> class Example(TypeCorrecting()):
>>>     a: int
>>>     b: datetime.date
>>> data = {
>>>     "a": "1",
>>>     "b": "2022-01-01"
>>> }
>>> example = Example(**data)
>>> example.a
1
>>> example.b
datetime.date(2022, 1, 1)
>>> isinstance(example, TypeCorrectingType)
True
>>> issubclass(Example,TypeCorrectingType)
True
```



