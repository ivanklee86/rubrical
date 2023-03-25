from typing import Optional

from pydantic import BaseModel

from rubrical.aenum import DependencySpecifications


class Package(BaseModel):
    name: str
    version: str
    specifier: Optional[DependencySpecifications]
