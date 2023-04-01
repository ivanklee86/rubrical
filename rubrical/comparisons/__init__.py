from rubrical.enum import PackageCheck, PackageTypes
from rubrical.schemas.configuration import PackageRequirement
from rubrical.schemas.package import Package

from . import semversion, string


def check_package(
    package_requirement: PackageRequirement, package: Package
) -> PackageCheck:
    result = None

    if package_requirement.type == PackageTypes.SEMVER:
        result = semversion.compare_package_semver(
            package=package, package_requirement=package_requirement
        )
    elif package_requirement.type == PackageTypes.GENERIC:
        result = string.compare_package_str(
            package=package, package_requirement=package_requirement
        )
    else:
        raise NotImplementedError("Comparison type not implemented.")

    return result
