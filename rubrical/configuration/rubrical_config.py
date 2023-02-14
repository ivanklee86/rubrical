from typing import List, Optional

from pydantic import BaseModel

from .dependency_manager import DependencyManager


class RubricalConfig(BaseModel):
    version: int
    blocking_mode: Optional[bool] = True
    dependency_managers: List[DependencyManager]
