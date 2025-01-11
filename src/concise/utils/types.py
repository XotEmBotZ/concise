from typing import TypeAlias, Union


TomlType: TypeAlias = dict[str, dict[str, Union[int, float, str, "TomlType"]]]
