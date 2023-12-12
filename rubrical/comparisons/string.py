from rubrical.comparisons.utils import results_to_status
from rubrical.enum import DependencySpecifications, PackageCheck
from rubrical.schemas.configuration import PackageRequirement
from rubrical.schemas.package import Package


def compare_package_str(
    package_requirement: PackageRequirement, package: Package
) -> PackageCheck:
    if (
        len(package.version_constraints) > 1
        or package.version_constraints[0].specifier != DependencySpecifications.EQ
    ):
        return PackageCheck.NOOP

    warn_signal = package_requirement.warn > package.version_constraints[0].version
    block_signal = package_requirement.block > package.version_constraints[0].version

    return results_to_status(warn_signal=warn_signal, block_signal=block_signal)
