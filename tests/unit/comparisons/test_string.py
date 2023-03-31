from rubrical.comparisons import string
from rubrical.enum import DependencySpecifications, PackageCheck
from rubrical.schemas.configuration import PackageRequirement
from rubrical.schemas.package import Package

SEMVER_PACKAGE_REQUIREMENT = PackageRequirement(
    **{"name": "dep1", "type": "semver", "warn": "v1.1.1", "block": "v1.0.0"}
)


def test_string():
    package = Package(
        name="dep1", version="v1.0.0", specifier=DependencySpecifications.EQ
    )

    result = string.compare_package_str(
        package=package, package_requirement=SEMVER_PACKAGE_REQUIREMENT
    )
    assert result == PackageCheck.BLOCK
