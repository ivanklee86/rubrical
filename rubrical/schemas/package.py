from typing import Optional

from pydantic import BaseModel

from rubrical.enum import DependencySpecifications


class Package(BaseModel):
    name: str
    version: str
    specifier: Optional[DependencySpecifications] = DependencySpecifications.EQ
