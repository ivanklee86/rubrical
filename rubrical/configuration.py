from typing import List, Optional

import semver
from pydantic import BaseModel, PrivateAttr

from rubrical.enum import PackageCheck, PackageTypes, SemverComparison


class PackageRequirement(BaseModel):
    name: str
    type: Optional[PackageTypes] = PackageTypes.SEMVER
    warn: str
    block: str
    _semver_warn: semver.VersionInfo = PrivateAttr
    _semver_block: semver.VersionInfo = PrivateAttr

    def __init__(self, **data) -> None:
        super().__init__(**data)

        if type == PackageTypes.SEMVER:
            self._semver_warn = semver.VersionInfo.parse(self.warn)
            self._semver_block = semver.VersionInfo.parse(self.block)

    def check_package(self, package) -> PackageCheck:
        if type == PackageTypes.SEMVER:
            package_semver = semver.VersionInfo.parse(package.version)
            warn_signal = SemverComparison.GT != semver.compare(
                package_semver, self._semver_warn
            )
            block_signal = SemverComparison.GT != semver.compare(
                package_semver, self._semver_block
            )
        else:
            warn_signal = self.warn >= package.version
            block_signal = self.block >= package.version

        if block_signal:
            status = PackageCheck.BLOCK
        elif warn_signal:
            status = PackageCheck.WARN
        else:
            status = PackageCheck.OK

        return status


class PackageManager(BaseModel):
    name: str
    packages: List[PackageRequirement]


class RubricalConfig(BaseModel):
    version: int
    blocking_mode: Optional[bool] = True
    package_managers: List[PackageManager]
