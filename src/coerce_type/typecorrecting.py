from dataclasses import fields

from coerce_type import coerce


def TypeCorrecting():
    def __post_init__(self):
        # noinspection PyDataclass,PyTypeChecker
        # making TypeCorrecting unnecessarily locks in certain choices
        my_fields = fields(self)
        for my_field in my_fields:
            object.__setattr__(self, my_field.name, coerce(self.__getattribute__(my_field.name), my_field.type))
    return type("TypeCorrecting", (object,), {"__post_init__": __post_init__})