from rubrical.comparisons.utils import results_to_status
from rubrical.enum import PackageCheck
from rubrical.schemas.configuration import PackageRequirement
from rubrical.schemas.package import Package


def compare_package_str(
    package_requirement: PackageRequirement, package: Package
) -> PackageCheck:
    warn_signal = package_requirement.warn >= package.version
    block_signal = package_requirement.block >= package.version

    return results_to_status(warn_signal=warn_signal, block_signal=block_signal)
