from typing import Tuple

from rubrical.comparisons.decorator import results
from rubrical.schemas.configuration import PackageRequirement
from rubrical.schemas.package import Package


@results
def _compare_package_str(
    package_requirement: PackageRequirement, package: Package
) -> Tuple[bool, bool]:
    warn_signal = package_requirement.warn >= package.version
    block_signal = package_requirement.block >= package.version

    return (warn_signal, block_signal)
