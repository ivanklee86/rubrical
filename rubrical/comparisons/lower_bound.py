"""
Grades a language version declaration by the lowest version it allows.

Each dialect follows its official specification, see
`docs/agents/plans/language-version-checks.md` for the rules and sources.
"""

import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from rubrical.comparisons.utils import results_to_status
from rubrical.enum import PackageCheck, VersionDialect
from rubrical.schemas.configuration import LanguageRequirement
from rubrical.schemas.language import LanguageDeclaration

Release = Tuple[int, int, int]

# All dialects allow whitespace between an operator and its version, e.g. `>= 3.8`.
OPERATOR_WHITESPACE = re.compile(r"(===|~=|==|!=|<>|<=|>=|<|>|=|\^|~)\s+")
COMPARATOR = re.compile(r"^(?P<op>===|~=|==|!=|<>|<=|>=|<|>|=|\^|~)?(?P<version>.*)$")
# Release numbers, then an optional wildcard, then an optional pre-release, post-release, dev or build suffix.
VERSION = re.compile(
    r"^v?(?P<release>\d+(?:\.\d+)*)"
    r"(?P<wildcard>(?:\.[xX*])*)"
    r"(?P<suffix>[-+][0-9A-Za-z.-]+|\.?[A-Za-z][0-9A-Za-z.]*)?$"
)
ANY_VERSION = re.compile(r"^v?[xX*](?:\.[xX*])*$")
NPM_HYPHEN_RANGE = re.compile(r"^(?P<low>\S+)\s+-\s+(?P<high>\S+)$")


class UngradeableError(ValueError):
    """A declaration that has no lower bound, or isn't valid in its dialect."""


@dataclass
class LanguageGrade:
    check: PackageCheck
    lower_bound: Optional[str]
    reason: str


@dataclass
class _Version:
    release: List[int]
    wildcard: bool
    suffix: bool

    def padded(self) -> Release:
        major, minor, patch = (self.release + [0, 0, 0])[:3]
        return (major, minor, patch)


def _parse_version(text: str) -> _Version:
    match = VERSION.match(text)
    if not match:
        raise UngradeableError(f"`{text}` is not a version")

    return _Version(
        release=[int(x) for x in match["release"].split(".")],
        wildcard=bool(match["wildcard"]),
        suffix=bool(match["suffix"]),
    )


def _split_comparator(comparator: str) -> Tuple[str, str]:
    match = COMPARATOR.match(comparator)
    assert match  # Every string matches; the operator is optional.
    return (match["op"] or "", match["version"])


def _exclusive(version: _Version) -> Release:
    # `>1.2.3-rc.1` and `>3.9rc1` still allow the release itself.
    if version.suffix:
        return version.padded()

    major, minor, patch = version.padded()
    return (major, minor, patch + 1)


def _go_comparator(comparator: str) -> Optional[Release]:
    op, text = _split_comparator(comparator)
    version = _parse_version(text.strip('"'))
    if op or version.wildcard or not 2 <= len(version.release) <= 3:
        raise UngradeableError(f"`{comparator}` is not a Go version")

    return version.padded()


def _npm_comparator(comparator: str) -> Optional[Release]:
    op, text = _split_comparator(comparator)
    if not text or ANY_VERSION.match(text):
        return None

    version = _parse_version(text)
    if op in ("<", "<="):
        return None
    if op == ">":
        # A partial version increments its last given part: `>1.2` := `>=1.3.0`.
        if version.wildcard or len(version.release) < 3:
            release = list(version.release)
            release[-1] += 1
            return _Version(release=release, wildcard=False, suffix=False).padded()
        return _exclusive(version)
    if op in ("", "=", ">=", "^", "~"):
        return version.padded()

    raise UngradeableError(f"`{op}` isn't an npm range operator")


def _pep440_comparator(comparator: str) -> Optional[Release]:
    op, text = _split_comparator(comparator)
    if op in ("", "^", "~", "=", "<>"):
        raise UngradeableError(f"`{comparator}` isn't a PEP 440 version specifier")
    if op == "===":
        raise UngradeableError("`===` arbitrary equality has no ordering")

    version = _parse_version(text)
    if version.wildcard and (op not in ("==", "!=") or not text.endswith(".*")):
        raise UngradeableError(f"`{comparator}` uses a wildcard outside `==`/`!=`")
    if op == "~=" and len(version.release) < 2:
        raise UngradeableError("`~=` needs at least two release segments")

    if op in ("<", "<=", "!="):
        return None
    if op == ">":
        return _exclusive(version)
    return version.padded()


def _poetry_comparator(comparator: str) -> Optional[Release]:
    op, text = _split_comparator(comparator)
    if ANY_VERSION.match(text) and op in ("", "=", "=="):
        return None
    if op == "===":
        raise UngradeableError("`===` arbitrary equality has no ordering")

    version = _parse_version(text)
    if version.wildcard and op not in ("", "=", "==", "!="):
        raise UngradeableError(f"`{comparator}` uses a wildcard with `{op}`")

    if op in ("<", "<=", "!=", "<>"):
        return None
    if op == ">":
        return _exclusive(version)
    return version.padded()


def _version_file_comparator(comparator: str) -> Optional[Release]:
    op, text = _split_comparator(comparator)
    version = _parse_version(text)
    if op or version.wildcard:
        raise UngradeableError(f"`{comparator}` is not a bare version")

    return version.padded()


def _python_version_file_comparator(comparator: str) -> Optional[Release]:
    op, _ = _split_comparator(comparator)
    if op:
        return _pep440_comparator(comparator)

    return _version_file_comparator(comparator)


def _go_alternatives(declaration: str) -> List[List[str]]:
    return [[declaration]]


def _npm_alternatives(declaration: str) -> List[List[str]]:
    alternatives = []
    for alternative in declaration.split("||"):
        if hyphen := NPM_HYPHEN_RANGE.match(alternative.strip()):
            alternatives.append([hyphen["low"]])
        else:
            alternatives.append(alternative.split())

    return alternatives


def _pep440_alternatives(declaration: str) -> List[List[str]]:
    if "|" in declaration:
        raise UngradeableError("PEP 440 has no OR operator")
    if not declaration:
        return [[]]

    comparators = [x.strip() for x in declaration.split(",")]
    if any(not x or re.search(r"\s", x) for x in comparators):
        raise UngradeableError("PEP 440 specifiers are separated by commas")

    return [comparators]


def _poetry_alternatives(declaration: str) -> List[List[str]]:
    return [
        [x for x in re.split(r"[\s,]+", alternative) if x]
        for alternative in re.split(r"\s*\|\|?\s*", declaration)
    ]


def _version_file_lines(declaration: str) -> List[str]:
    # An empty declaration is one empty line, which isn't a version.
    return declaration.splitlines() or [""]


def _version_file_alternatives(declaration: str) -> List[List[str]]:
    # Version managers make every listed version available, so each line is an alternative.
    return [[line] for line in _version_file_lines(declaration)]


def _python_version_file_alternatives(declaration: str) -> List[List[str]]:
    # uv also accepts a PEP 440 specifier set on a line, e.g. `>=3.12,<3.13`.
    return [
        _pep440_alternatives(line)[0] if _split_comparator(line)[0] else [line]
        for line in _version_file_lines(declaration)
    ]


DIALECTS: Dict[
    VersionDialect,
    Tuple[Callable[[str], List[List[str]]], Callable[[str], Optional[Release]]],
] = {
    VersionDialect.GO: (_go_alternatives, _go_comparator),
    VersionDialect.NPM: (_npm_alternatives, _npm_comparator),
    VersionDialect.PEP440: (_pep440_alternatives, _pep440_comparator),
    VersionDialect.POETRY: (_poetry_alternatives, _poetry_comparator),
    VersionDialect.VERSION_FILE: (
        _version_file_alternatives,
        _version_file_comparator,
    ),
    VersionDialect.PYTHON_VERSION_FILE: (
        _python_version_file_alternatives,
        _python_version_file_comparator,
    ),
}


def _format(release: Release) -> str:
    return ".".join(str(x) for x in release)


def lower_bound(declaration: str, dialect: VersionDialect) -> str:
    """
    Returns the lowest `MAJOR.MINOR.PATCH` release a declaration allows.

    Raises `UngradeableError` when the declaration has no lower bound or isn't valid in the dialect.
    """
    split_alternatives, comparator_lower_bound = DIALECTS[dialect]
    normalized = OPERATOR_WHITESPACE.sub(r"\1", declaration.strip())

    alternative_bounds: List[Release] = []
    for comparators in split_alternatives(normalized):
        # Comparators are ANDed, so the highest lower bound applies.
        bounds = [
            bound
            for comparator in comparators
            if (bound := comparator_lower_bound(comparator)) is not None
        ]
        if not bounds:
            raise UngradeableError(f"`{declaration}` has no lower bound")
        alternative_bounds.append(max(bounds))

    # Alternatives are ORed, so the lowest lower bound applies.
    return _format(min(alternative_bounds))


def compare_language(
    requirement: LanguageRequirement, declaration: LanguageDeclaration
) -> LanguageGrade:
    try:
        bound = lower_bound(declaration.version, declaration.dialect)
        warn = _parse_version(requirement.warn).padded()
        block = _parse_version(requirement.block).padded()
    except UngradeableError as e:
        return LanguageGrade(check=PackageCheck.NOOP, lower_bound=None, reason=str(e))

    release = _parse_version(bound).padded()
    check = results_to_status(warn_signal=release < warn, block_signal=release < block)

    return LanguageGrade(
        check=check,
        lower_bound=bound,
        reason=f"lower bound {bound} (warn {_format(warn)}, block {_format(block)})",
    )
