from enum import Enum


class SemverComparison(Enum):
    LT = -1
    GT = 1
    EQ = 0


class PackageTypes(Enum):
    SEMVER = "semver"
    GENERIC = "generic"


class PackageCheck(Enum):
    OK = "ok"
    WARN = "warn"
    BLOCK = "block"


class SupportedPackageManagers(Enum):
    JSONNET = "jsonnet"
    PYTHON = "python"
