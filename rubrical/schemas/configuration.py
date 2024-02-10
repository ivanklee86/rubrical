from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from rubrical.enum import PackageTypes, SupportedPackageManagers


class PackageRequirement(BaseModel):
    name: str
    type: Optional[PackageTypes] = PackageTypes.SEMVER
    warn: str
    block: str


class PackageManager(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    name: SupportedPackageManagers
    packages: List[PackageRequirement]


class RubricalConfig(BaseModel):
    version: int
    blocking_mode: Optional[bool] = True
    package_managers: List[PackageManager]
