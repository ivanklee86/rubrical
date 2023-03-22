from dataclasses import dataclass

from rubrical.enum import PackageCheck


@dataclass
class PackageCheckResult:
    name: str
    file: str
    check: PackageCheck
    version_package: str
    version_block: str
    version_warn: str
