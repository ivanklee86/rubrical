# import semver
# from typing import Tuple

# from rubrical.enum import PackageCheck, PackageTypes, SemverComparison
# from rubrical.schemas.configuration import PackageRequirement
# from rubrical.schemas.package import Package
# from rubrical.comparisons.decorator import results


# def __semver_conversion(version: str):
#     return version[1:] if version.startswith("v") else version

# @results
# def _compare_package_semver(
#     package_requirement: PackageRequirement, package: Package
# ) -> Tuple[bool, bool]:
#     if package.specifier in []

#     try:
#         warn_signal = SemverComparison.GT.value != semver.compare(
#             package_semver,
#             __semver_conversion(package_requirement.warn),
#         )
#         block_signal = SemverComparison.GT.value != semver.compare(
#             package_semver,
#             __semver_conversion(package_requirement.block),
#         )
#     except ValueError:
#         warn_signal = False
#         block_signal = False

#     return (warn_signal, block_signal)
