from rubrical.configuration import PackageRequirement
from rubrical.enum import PackageCheck
from rubrical.package import Package

SEMVER_PACKAGE_REQUIREMENT = PackageRequirement(
    **{"name": "dep1", "type": "semver", "warn": "v1.0.1", "block": "v1.0.0"}
)

SEMVER_PACKAGE = Package(**{"name": "dep1", "version": "v1.0.0"})
SEMVER_OLD_PACKAGE = Package(**{"name": "dep1", "version": "v0.9.0"})
SEMVER_NEWER_PACKAGE = Package(**{"name": "dep1", "version": "v1.0.1"})
SEMVER_NEWEST_PACKAGE = Package(**{"name": "dep2", "version": "v1.0.2"})


def test_dependency_semver():
    assert PackageCheck.BLOCK == SEMVER_PACKAGE_REQUIREMENT.check_package(
        SEMVER_OLD_PACKAGE
    )
    assert PackageCheck.BLOCK == SEMVER_PACKAGE_REQUIREMENT.check_package(
        SEMVER_PACKAGE
    )
    assert PackageCheck.WARN == SEMVER_PACKAGE_REQUIREMENT.check_package(
        SEMVER_NEWER_PACKAGE
    )
    assert PackageCheck.OK == SEMVER_PACKAGE_REQUIREMENT.check_package(
        SEMVER_NEWEST_PACKAGE
    )


def test_dependency_actuallysemver():
    requirement = PackageRequirement(
        **{"name": "dep1", "type": "semver", "warn": "v1.11.1", "block": "v1.11.0"}
    )

    package = Package(**{"name": "dep1", "version": "v1.7.0"})

    assert PackageCheck.BLOCK == requirement.check_package(package)
