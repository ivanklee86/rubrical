from enum import Enum


class SemverComparison(Enum):
    LT = -1
    GT = 1
    EQ = 0


class DependencySpecifications(Enum):
    EQ = "EQ"
    GT = "GT"
    GTE = "GTE"
    LT = "LT"
    LTE = "LTE"
    NE = "NE"
    COMPATIBLE = "COMPATIBLE"


class PackageTypes(Enum):
    SEMVER = "semver"
    GENERIC = "generic"


class PackageCheck(Enum):
    OK = "ok"
    WARN = "warn"
    BLOCK = "block"
    NOOP = "noop"


class SupportedPackageManagers(Enum):
    JSONNET = "jsonnet"
    PYTHON = "python"
