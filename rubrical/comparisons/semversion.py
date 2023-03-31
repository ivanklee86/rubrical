import semver

from rubrical.comparisons.utils import results_to_status
from rubrical.enum import (
    DependencySpecifications,
    PackageCheck,
    SemverComparison,
)
from rubrical.schemas.configuration import PackageRequirement
from rubrical.schemas.package import Package


def __semver_conversion(version: str):
    return version[1:] if version.startswith("v") else version


def compare_package_semver(
    package_requirement: PackageRequirement, package: Package
) -> PackageCheck:
    result = None

    if package.specifier in [
        DependencySpecifications.EQ,
        DependencySpecifications.LT,
        DependencySpecifications.LTE,
    ]:
        package_semver = __semver_conversion(package.version)
    elif package.specifier in [
        DependencySpecifications.NE,
        DependencySpecifications.GT,
        DependencySpecifications.GTE,
    ]:
        result = PackageCheck.NOOP
    elif package.specifier == DependencySpecifications.COMPATIBLE:
        parsed_version = __semver_conversion(package.version).split(".")
        if len(parsed_version) < 3:
            parsed_version += ["999999"] * (3 - len(parsed_version))
        package_semver = ".".join(parsed_version)

    if not result:
        try:
            warn_signal = SemverComparison.GT.value != semver.compare(
                package_semver,
                __semver_conversion(package_requirement.warn),
            )
            block_signal = SemverComparison.GT.value != semver.compare(
                package_semver,
                __semver_conversion(package_requirement.block),
            )
        except ValueError:
            warn_signal = False
            block_signal = False

        result = results_to_status(warn_signal=warn_signal, block_signal=block_signal)

    return result
