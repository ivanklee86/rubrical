from rubrical.comparisons import check_package
from rubrical.enum import PackageCheck
from rubrical.schemas.configuration import PackageRequirement
from rubrical.schemas.package import Package

SEMVER_PACKAGE_REQUIREMENT = PackageRequirement(
    **{"name": "dep1", "type": "semver", "warn": "v1.0.1", "block": "v1.0.0"}
)

GENERIC_PACKAGE_REQUIREMENT = PackageRequirement(
    **{"name": "dep1", "type": "generic", "warn": "v1.0.1", "block": "v1.0.0"}
)

SEMVER_PACKAGE = Package(**{"name": "dep1", "version": "v1.0.0"})
SEMVER_OLD_PACKAGE = Package(**{"name": "dep1", "version": "v0.9.0"})
SEMVER_NEWER_PACKAGE = Package(**{"name": "dep1", "version": "v1.0.1"})
SEMVER_NEWEST_PACKAGE = Package(**{"name": "dep2", "version": "v1.0.2"})


def test_dependency_semver():
    assert PackageCheck.BLOCK == check_package(
        SEMVER_PACKAGE_REQUIREMENT, SEMVER_OLD_PACKAGE
    )
    assert PackageCheck.BLOCK == check_package(
        SEMVER_PACKAGE_REQUIREMENT, SEMVER_PACKAGE
    )
    assert PackageCheck.WARN == check_package(
        SEMVER_PACKAGE_REQUIREMENT, SEMVER_NEWER_PACKAGE
    )
    assert PackageCheck.OK == check_package(
        SEMVER_PACKAGE_REQUIREMENT, SEMVER_NEWEST_PACKAGE
    )


def test_dependency_generic():
    assert PackageCheck.BLOCK == check_package(
        GENERIC_PACKAGE_REQUIREMENT, SEMVER_OLD_PACKAGE
    )


def test_dependency_actuallysemver():
    requirement = PackageRequirement(
        **{"name": "dep1", "type": "semver", "warn": "v1.11.1", "block": "v1.11.0"}
    )

    package = Package(**{"name": "dep1", "version": "v1.7.0"})

    assert PackageCheck.BLOCK == check_package(requirement, package)


def test_dependency_branch():
    requirement = PackageRequirement(
        **{"name": "dep1", "type": "semver", "warn": "v1.11.1", "block": "v1.11.0"}
    )

    package = Package(**{"name": "dep1", "version": "some-random-branch"})

    assert PackageCheck.OK == check_package(requirement, package)
