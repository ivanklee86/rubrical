from pydantic import BaseModel

from rubrical.enum import ComparisonOperators


class DependencyRequirement(BaseModel):
    name: str
    comparison: ComparisonOperators
    warn: str
    block: str

    def silly_function(self):
        print(self.name)
        print(self.comparison)
