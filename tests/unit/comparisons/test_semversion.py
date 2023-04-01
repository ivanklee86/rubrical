from rubrical.comparisons import semversion
from rubrical.enum import DependencySpecifications, PackageCheck
from rubrical.schemas.configuration import PackageRequirement
from rubrical.schemas.package import Package

SEMVER_PACKAGE_REQUIREMENT = PackageRequirement(
    **{"name": "dep1", "type": "semver", "warn": "v1.10.1", "block": "v1.0.0"}
)


def test_semver_eq():
    package = Package(
        name="dep1", version="v1.0.0", specifier=DependencySpecifications.EQ
    )

    result = semversion.compare_package_semver(
        package=package, package_requirement=SEMVER_PACKAGE_REQUIREMENT
    )
    assert result == PackageCheck.BLOCK


def test_semver_gt():
    package = Package(
        name="dep1", version="v1.0.0", specifier=DependencySpecifications.GT
    )

    result = semversion.compare_package_semver(
        package=package, package_requirement=SEMVER_PACKAGE_REQUIREMENT
    )
    assert result == PackageCheck.NOOP


def test_semver_compatable():
    package = Package(
        name="dep1", version="1", specifier=DependencySpecifications.COMPATIBLE
    )

    result = semversion.compare_package_semver(
        package=package, package_requirement=SEMVER_PACKAGE_REQUIREMENT
    )
    assert result == PackageCheck.OK


def test_semver_warn():
    package = Package(
        name="dep1", version="1.7", specifier=DependencySpecifications.COMPATIBLE
    )

    result = semversion.compare_package_semver(
        package=package, package_requirement=SEMVER_PACKAGE_REQUIREMENT
    )
    assert result == PackageCheck.WARN
