from rubrical.comparisons import check_package
from rubrical.enum import DependencySpecifications, PackageCheck
from rubrical.schemas.configuration import PackageRequirement
from rubrical.schemas.package import Package, Specification

SEMVER_PACKAGE_REQUIREMENT = PackageRequirement(
    **{"name": "dep1", "type": "semver", "warn": "v1.0.1", "block": "v1.0.0"}
)

GENERIC_PACKAGE_REQUIREMENT = PackageRequirement(
    **{"name": "dep1", "type": "generic", "warn": "v1.0.1", "block": "v1.0.0"}
)

SEMVER_PACKAGE = Package(
    name="dep1",
    raw_constraint="",
    version_constraints=[
        Specification(version="v1.0.0", specifier=DependencySpecifications.EQ)
    ],
)
SEMVER_OLD_PACKAGE = Package(
    name="dep1",
    raw_constraint="",
    version_constraints=[
        Specification(version="v0.9.0", specifier=DependencySpecifications.EQ)
    ],
)
SEMVER_NEWER_PACKAGE = Package(
    name="dep1",
    raw_constraint="",
    version_constraints=[
        Specification(version="v1.0.1", specifier=DependencySpecifications.EQ)
    ],
)
SEMVER_NEWEST_PACKAGE = Package(
    name="dep1",
    raw_constraint="",
    version_constraints=[
        Specification(version="v1.0.2", specifier=DependencySpecifications.EQ)
    ],
)


def test_dependency_semver():
    assert PackageCheck.BLOCK == check_package(
        SEMVER_PACKAGE_REQUIREMENT, SEMVER_OLD_PACKAGE
    )
    assert PackageCheck.WARN == check_package(
        SEMVER_PACKAGE_REQUIREMENT, SEMVER_PACKAGE
    )
    assert PackageCheck.OK == check_package(
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

    package = Package(
        name="dep1",
        raw_constraint="",
        version_constraints=[
            Specification(version="v1.7.0", specifier=DependencySpecifications.EQ)
        ],
    )

    assert PackageCheck.BLOCK == check_package(requirement, package)


def test_dependency_branch():
    requirement = PackageRequirement(
        **{"name": "dep1", "type": "semver", "warn": "v1.11.1", "block": "v1.11.0"}
    )

    package = Package(
        name="dep1",
        raw_constraint="",
        version_constraints=[
            Specification(
                version="some-random-branch", specifier=DependencySpecifications.EQ
            )
        ],
    )

    assert PackageCheck.OK == check_package(requirement, package)
