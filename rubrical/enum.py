from enum import Enum


class ComparisonOperators(Enum):
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="


class SemverComparison(Enum):
    LT = -1
    GT = 1
    EQ = 0


class DependencyTypes(Enum):
    SEMVER = "semver"
    GENERIC = "generic"


class DependencyCheck(Enum):
    OK = "ok"
    WARN = "warn"
    BLOCK = "block"
