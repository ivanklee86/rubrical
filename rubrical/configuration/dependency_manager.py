from typing import List

from pydantic import BaseModel

from .dependency_requirement import DependencyRequirement


class DependencyManager(BaseModel):
    name: str
    dependencies: List[DependencyRequirement]
