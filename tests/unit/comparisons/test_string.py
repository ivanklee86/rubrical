from rubrical.comparisons import string
from rubrical.enum import DependencySpecifications, PackageCheck
from rubrical.schemas.configuration import PackageRequirement
from rubrical.schemas.package import Package, Specification

SEMVER_PACKAGE_REQUIREMENT = PackageRequirement(
    **{"name": "dep1", "type": "semver", "warn": "v1.1.1", "block": "v1.0.0"}
)


def test_string_block():
    package = Package(
        name="dep1",
        raw_constraint="",
        version_constraints=[
            Specification(version="v0.9.0", specifier=DependencySpecifications.EQ)
        ],
    )

    result = string.compare_package_str(
        package=package, package_requirement=SEMVER_PACKAGE_REQUIREMENT
    )
    assert result == PackageCheck.BLOCK


def test_string_warn():
    package = Package(
        name="dep1",
        raw_constraint="",
        version_constraints=[
            Specification(version="v1.0.0", specifier=DependencySpecifications.EQ)
        ],
    )

    result = string.compare_package_str(
        package=package, package_requirement=SEMVER_PACKAGE_REQUIREMENT
    )
    assert result == PackageCheck.WARN


def test_string_noop():
    package = Package(
        name="dep1",
        raw_constraint="",
        version_constraints=[
            Specification(version="v1.0.0", specifier=DependencySpecifications.GT),
            Specification(version="v2.0.0", specifier=DependencySpecifications.LT),
        ],
    )

    result = string.compare_package_str(
        package=package, package_requirement=SEMVER_PACKAGE_REQUIREMENT
    )
    assert result == PackageCheck.NOOP
