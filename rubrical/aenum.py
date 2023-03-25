from typing import TYPE_CHECKING

if TYPE_CHECKING:
    #! This is only processed by MyPy (i.e. not at runtime)
    from enum import Enum
else:
    #! This is real runtime code.
    from aenum import Enum


class DependencySpecifications(Enum):
    EQ = "=="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
