from typing import Optional

import semver
from pydantic import BaseModel, PrivateAttr

from rubrical.enum import DependencyCheck, DependencyTypes, SemverComparison


class DependencyRequirement(BaseModel):
    type: Optional[DependencyTypes] = DependencyTypes.SEMVER
    warn: str
    block: str
    _semver_warn: semver.VersionInfo = PrivateAttr
    _semver_block: semver.VersionInfo = PrivateAttr

    def __init__(self, **data) -> None:
        super().__init__(**data)

        if type == DependencyTypes.SEMVER:
            self._semver_warn = semver.VersionInfo.parse(self.warn)
            self._semver_block = semver.VersionInfo.parse(self.block)

    def check_dependency(self, dependency) -> bool:
        if type == DependencyTypes.SEMVER:
            dependency_semver = semver.VersionInfo.parse(dependency.version)
            warn_signal = SemverComparison.GT != semver.compare(
                dependency_semver, self._semver_warn
            )
            block_signal = SemverComparison.GT != semver.compare(
                dependency_semver, self._semver_block
            )
        else:
            warn_signal = self.warn >= dependency.version
            block_signal = self.block >= dependency.version

        if block_signal:
            status = DependencyCheck.BLOCK
        elif warn_signal:
            status = DependencyCheck.WARN
        else:
            status = DependencyCheck.OK

        return status
