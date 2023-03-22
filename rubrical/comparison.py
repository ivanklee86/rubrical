import semver

from rubrical.enum import PackageCheck, PackageTypes, SemverComparison
from rubrical.schemas.configuration import PackageRequirement
from rubrical.schemas.package import Package


def check_package(
    package_requirement: PackageRequirement, package: Package
) -> PackageCheck:
    if package_requirement.type == PackageTypes.SEMVER:
        package_semver = (
            package.version[1:] if package.version.startswith("v") else package.version
        )

        try:
            warn_signal = SemverComparison.GT.value != semver.compare(
                package_semver,
                package_requirement.warn[1:]
                if package_requirement.warn.startswith("v")
                else package_requirement.warn,
            )
            block_signal = SemverComparison.GT.value != semver.compare(
                package_semver,
                package_requirement.block[1:]
                if package_requirement.block.startswith("v")
                else package_requirement.block,
            )
        except ValueError:
            warn_signal = False
            block_signal = False
    else:
        warn_signal = package_requirement.warn >= package.version
        block_signal = package_requirement.block >= package.version

    if block_signal:
        status = PackageCheck.BLOCK
    elif warn_signal:
        status = PackageCheck.WARN
    else:
        status = PackageCheck.OK

    return status
