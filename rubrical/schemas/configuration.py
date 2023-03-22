from typing import List, Optional

from pydantic import BaseModel

from rubrical.enum import PackageTypes


class PackageRequirement(BaseModel):
    name: str
    type: Optional[PackageTypes] = PackageTypes.SEMVER
    warn: str
    block: str


class PackageManager(BaseModel):
    name: str
    packages: List[PackageRequirement]


class RubricalConfig(BaseModel):
    version: int
    blocking_mode: Optional[bool] = True
    package_managers: List[PackageManager]
