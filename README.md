# coerce_type

coerce_type is a library for the type coercion of values 
to the annotations they have. It can be triggered manually with `coerce`
or be set to happen automatically for a dataclass by having it inherit a `TypeCorrecting` class

## Installation

Currently only a manual installation is possible, but an upload to pip is planned.
```shell
git clone git@github.com:reyemDarnok/coerce_type.git
cd coerce_type
hatch build
pip install ./dist/coerce_type-1.0.2-py3-none-any.whl
```

