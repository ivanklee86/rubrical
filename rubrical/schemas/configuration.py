from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from rubrical.enum import PackageTypes, SupportedLanguages, SupportedPackageManagers


class PackageRequirement(BaseModel):
    name: str
    type: Optional[PackageTypes] = PackageTypes.SEMVER
    warn: str
    block: str


class PackageManager(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    name: SupportedPackageManagers
    packages: List[PackageRequirement]


class LanguageRequirement(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    name: SupportedLanguages
    warn: str
    block: str


class RubricalConfig(BaseModel):
    version: int
    blocking_mode: bool = True
    languages: List[LanguageRequirement] = []
    package_managers: List[PackageManager] = []

    @field_validator("languages")
    @classmethod
    def unique_languages(
        cls, languages: List[LanguageRequirement]
    ) -> List[LanguageRequirement]:
        names = [str(x.name) for x in languages]
        duplicates = sorted({x for x in names if names.count(x) > 1})
        if duplicates:
            raise ValueError(f"Languages may only be configured once: {duplicates}")

        return languages
