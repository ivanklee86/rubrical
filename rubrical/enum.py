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
    APPROX_EQ = "APPROX_EQ"


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
    GO = "go"
    NODEJS = "nodejs"


class SupportedLanguages(Enum):
    PYTHON = "python"
    GO = "go"
    NODEJS = "nodejs"


class VersionDialect(Enum):
    GO = "go"
    PEP440 = "pep440"
    POETRY = "poetry"
    NPM = "npm"
    # One bare version per line, e.g. `.nvmrc`.
    VERSION_FILE = "version_file"
    # One bare version or PEP 440 specifier set per line, e.g. `.python-version`.
    PYTHON_VERSION_FILE = "python_version_file"
