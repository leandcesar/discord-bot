import typing as t
from dataclasses import fields, is_dataclass

T = t.TypeVar("T")


def to_instance(data: dict, cls: type[T]) -> T:
    if not is_dataclass(cls):
        raise TypeError(f"{cls.__name__} is not a dataclass.")
    class_fields = {f.name for f in fields(cls)}
    filtered_data = {key: value for key, value in data.items() if key in class_fields}
    return t.cast(T, cls(**filtered_data))
