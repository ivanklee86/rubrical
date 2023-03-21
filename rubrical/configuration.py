from typing import List, Optional

import semver
from pydantic import BaseModel

from rubrical.enum import PackageCheck, PackageTypes, SemverComparison


class PackageRequirement(BaseModel):
    name: str
    type: Optional[PackageTypes] = PackageTypes.SEMVER
    warn: str
    block: str

    def check_package(self, package) -> PackageCheck:
        if self.type == PackageTypes.SEMVER:
            package_semver = (
                package.version[1:]
                if package.version.startswith("v")
                else package.version
            )

            warn_signal = SemverComparison.GT.value != semver.compare(
                package_semver,
                self.warn[1:] if self.warn.startswith("v") else self.warn,
            )
            block_signal = SemverComparison.GT.value != semver.compare(
                package_semver,
                self.block[1:] if self.block.startswith("v") else self.block,
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
