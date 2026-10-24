import pytest

from rubrical.comparisons.lower_bound import (
    UngradeableError,
    compare_language,
    lower_bound,
)
from rubrical.enum import PackageCheck, VersionDialect
from rubrical.schemas.configuration import LanguageRequirement
from rubrical.schemas.language import LanguageDeclaration

GO = VersionDialect.GO
PEP440 = VersionDialect.PEP440
POETRY = VersionDialect.POETRY
NPM = VersionDialect.NPM


@pytest.mark.parametrize(
    "dialect,declaration,expected",
    [
        # Go: a bare version; `1.21` and `1.21rc1` both precede `1.21.0`.
        (GO, "1.19", "1.19.0"),
        (GO, "1.21.3", "1.21.3"),
        (GO, "1.21rc1", "1.21.0"),
        # PEP 440: comma-separated clauses, zero padded.
        (PEP440, ">=3.7", "3.7.0"),
        (PEP440, "~=3.10", "3.10.0"),
        (PEP440, "==3.12.*", "3.12.0"),
        (PEP440, "==3.12", "3.12.0"),
        (PEP440, ">=v3.8", "3.8.0"),
        (PEP440, ">3.9", "3.9.1"),
        (PEP440, ">= 3.8", "3.8.0"),
        (PEP440, ">=3.9,<4", "3.9.0"),
        (PEP440, ">=3.8, >=3.10", "3.10.0"),
        (PEP440, ">=3.13.0rc1", "3.13.0"),
        # Poetry: PEP 440 plus `^`, `~`, whitespace AND, and `||`/`|` OR.
        (POETRY, "^3.12", "3.12.0"),
        (POETRY, "~3.12", "3.12.0"),
        (POETRY, "3.*", "3.0.0"),
        (POETRY, "3.12", "3.12.0"),
        (POETRY, ">3.9", "3.9.1"),
        (POETRY, ">=3.8 <4.0", "3.8.0"),
        (POETRY, ">=3.8,<4.0", "3.8.0"),
        (POETRY, "^3.9 || ^3.11", "3.9.0"),
        (POETRY, "^3.11 | ^3.9", "3.9.0"),
        # npm: node-semver ranges.
        (NPM, ">=18.0.0", "18.0.0"),
        (NPM, "^20.11.0", "20.11.0"),
        (NPM, "~18.2", "18.2.0"),
        (NPM, "20.x", "20.0.0"),
        (NPM, "20", "20.0.0"),
        (NPM, "=20.1.0", "20.1.0"),
        (NPM, "v20.1.0", "20.1.0"),
        (NPM, ">1", "2.0.0"),
        (NPM, ">18.2", "18.3.0"),
        (NPM, ">18.2.3", "18.2.4"),
        (NPM, ">18.x", "19.0.0"),
        (NPM, ">=18.17.0 <23", "18.17.0"),
        (NPM, ">= 18.17.0", "18.17.0"),
        (NPM, "1.2 - 2.3.4", "1.2.0"),
        (NPM, "20.0.0-rc.1", "20.0.0"),
        (NPM, "^18.18.0 || ^20.9.0 || >=21.1.0", "18.18.0"),
        (NPM, ">=21.1.0 || ^20.9.0 || ^18.18.0", "18.18.0"),
    ],
)
def test_lower_bound(dialect, declaration, expected):
    assert lower_bound(declaration, dialect) == expected


@pytest.mark.parametrize(
    "dialect,declaration",
    [
        # No lower bound.
        (PEP440, "<3.12"),
        (PEP440, "!=3.9.*"),
        (PEP440, ""),
        (POETRY, "*"),
        (NPM, "*"),
        (NPM, "x"),
        (NPM, ""),
        (NPM, "<16"),
        (NPM, "^18 || <16"),
        # Not valid in the dialect.
        (GO, ">=1.19"),
        (GO, "1"),
        (PEP440, "^3.12"),
        (PEP440, "3.12"),
        (PEP440, "~=3"),
        (PEP440, ">=3.*"),
        (PEP440, "===3.12"),
        (PEP440, ">=3.8 || >=3.9"),
        (PEP440, ">=3.8 <4"),
        (NPM, "~=1.2"),
        # Not a version.
        (GO, "banana"),
        (PEP440, ">=banana"),
        (POETRY, "banana"),
        (NPM, "banana"),
    ],
)
def test_lower_bound_ungradeable(dialect, declaration):
    with pytest.raises(UngradeableError):
        lower_bound(declaration, dialect)


REQUIREMENT = LanguageRequirement(name="python", warn="v3.12.0", block="v3.10.0")


def _declaration(version: str) -> LanguageDeclaration:
    return LanguageDeclaration(
        version=version, raw_constraint=version, dialect=VersionDialect.PEP440
    )


@pytest.mark.parametrize(
    "version,expected",
    [
        (">=3.9", PackageCheck.BLOCK),
        (">=3.10", PackageCheck.WARN),
        (">=3.11", PackageCheck.WARN),
        (">=3.12", PackageCheck.OK),
        (">=3.13", PackageCheck.OK),
        # Ungradeable declarations are never OK.
        ("<3.12", PackageCheck.NOOP),
        ("^3.12", PackageCheck.NOOP),
    ],
)
def test_compare_language(version, expected):
    grade = compare_language(REQUIREMENT, _declaration(version))

    assert grade.check == expected


def test_compare_language_explains_result():
    grade = compare_language(REQUIREMENT, _declaration(">=3.9"))
    assert grade.lower_bound == "3.9.0"
    assert "3.9.0" in grade.reason

    grade = compare_language(REQUIREMENT, _declaration("<3.12"))
    assert grade.lower_bound is None
    assert "no lower bound" in grade.reason


def test_compare_language_unparseable_threshold_is_noop():
    requirement = LanguageRequirement(name="python", warn="latest", block="v3.10.0")

    grade = compare_language(requirement, _declaration(">=3.9"))

    assert grade.check == PackageCheck.NOOP
    assert "latest" in grade.reason
