from typing import Union, Sequence, List

PJSValueTypes = Union[None, bool, int, float, complex, str, bytes]
PJSContainers = Sequence[PJSValueTypes]
PJSValues = Union[PJSContainers, PJSValueTypes]
TagType = List[str]
