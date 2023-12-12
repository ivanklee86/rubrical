from typing import List

import semver

from rubrical.comparisons.utils import max_status, results_to_status
from rubrical.enum import (
    DependencySpecifications,
    PackageCheck,
    SemverComparison,
)
from rubrical.schemas.configuration import PackageRequirement
from rubrical.schemas.package import Package, Specification


def __semver_conversion(version: str):
    return version[1:] if version.startswith("v") else version


def __evaluate_specification(
    package_requirement: PackageRequirement, specification: Specification
) -> PackageCheck:
    result = None

    if specification.specifier in [
        DependencySpecifications.EQ,
        DependencySpecifications.LT,
        DependencySpecifications.LTE,
    ]:
        package_semver = __semver_conversion(specification.version)
    elif specification.specifier in [
        DependencySpecifications.NE,
        DependencySpecifications.GT,
        DependencySpecifications.GTE,
    ]:
        result = PackageCheck.NOOP
    elif specification.specifier == DependencySpecifications.APPROX_EQ:
        parsed_version = __semver_conversion(specification.version).split(".")
        if len(parsed_version) < 3:
            parsed_version += ["999999"] * (3 - len(parsed_version))
        package_semver = ".".join(parsed_version)
    elif specification.specifier == DependencySpecifications.COMPATIBLE:
        parsed_version = __semver_conversion(specification.version).split(".")
        for idx in reversed(range(len(parsed_version))):
            if parsed_version[idx]:
                parsed_version[idx] = "999999"
                break
        if len(parsed_version) < 3:
            parsed_version += ["999999"] * (3 - len(parsed_version))
        package_semver = ".".join(parsed_version)

    if not result:
        try:
            warn_signal = SemverComparison.LT.value == semver.compare(
                package_semver,
                __semver_conversion(package_requirement.warn),
            )
            block_signal = SemverComparison.LT.value == semver.compare(
                package_semver,
                __semver_conversion(package_requirement.block),
            )
        except ValueError:
            warn_signal = False
            block_signal = False

        result = results_to_status(warn_signal=warn_signal, block_signal=block_signal)

    return result


def compare_package_semver(
    package_requirement: PackageRequirement, package: Package
) -> PackageCheck:
    raw_result: List[PackageCheck] = list(
        map(
            lambda x: __evaluate_specification(package_requirement, x),
            package.version_constraints,
        )
    )

    return max_status(raw_result)
