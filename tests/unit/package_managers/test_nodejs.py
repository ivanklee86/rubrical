import json
from pathlib import Path

from rubrical.comparisons import check_package
from rubrical.enum import DependencySpecifications, PackageCheck
from rubrical.package_managers.base_package_manager import PackageManagerFileDetails
from rubrical.package_managers.nodejs import NodeJS
from rubrical.schemas.configuration import PackageRequirement
from tests.constants import FILES_FOLDER_PATH


def test_nodejs():
    nodejs = NodeJS()

    nodejs.read_package_manager_files(Path(FILES_FOLDER_PATH, "nodejs"))
    nodejs.parse_package_manager_files()

    assert len(nodejs.packages["package.json"]) == 104
    assert len(nodejs.packages["complex/package.json"]) == 11
    assert "node_modules/buffer/package.json" not in nodejs.packages

    # Check single version specifiers.
    [dep] = [x for x in nodejs.packages["complex/package.json"] if x.name == "til"]
    assert dep.version_constraints[0].version == "1.2"
    assert dep.version_constraints[0].specifier == DependencySpecifications.APPROX_EQ

    # Check for multiple version specifiers in dash-based ranges
    [dep] = [x for x in nodejs.packages["complex/package.json"] if x.name == "foo"]
    assert dep.version_constraints[0].version == "1.0.0"
    assert dep.version_constraints[0].specifier == DependencySpecifications.GTE
    assert dep.version_constraints[1].version == "2.9999.9999"
    assert dep.version_constraints[1].specifier == DependencySpecifications.LTE

    # Check for multiple version specifiers in dash-based ranges
    [dep] = [x for x in nodejs.packages["complex/package.json"] if x.name == "baz"]
    assert dep.version_constraints[0].version == "1.0.2"
    assert dep.version_constraints[0].specifier == DependencySpecifications.GT
    assert dep.version_constraints[1].version == "2.3.4"
    assert dep.version_constraints[1].specifier == DependencySpecifications.LTE


def _parse_dependencies(dependencies: dict) -> dict:
    nodejs = NodeJS()
    nodejs.parse_package_manager_file(
        PackageManagerFileDetails(
            name="package.json",
            path=Path("package.json"),
            contents=json.dumps({"dependencies": dependencies}),
        )
    )

    return {x.name: x for x in nodejs.packages["package.json"]}


def _specifications(package):
    return [(x.version, x.specifier) for x in package.version_constraints]


def test_nodejs_whitespace_after_operator():
    # node-semver trims whitespace between an operator and its version.
    packages = _parse_dependencies(
        {
            "gte": ">= 1.2.3",
            "range": "> 1.0.2 <= 2.3.4",
            "caret": "^ 1.2.3",
            "tilde": "~ 1.2.3",
            "hyphen": "1.0.0 - 2.0.0",
        }
    )

    assert _specifications(packages["gte"]) == [("1.2.3", DependencySpecifications.GTE)]
    assert _specifications(packages["range"]) == [
        ("1.0.2", DependencySpecifications.GT),
        ("2.3.4", DependencySpecifications.LTE),
    ]
    assert _specifications(packages["caret"]) == [
        ("1.2.3", DependencySpecifications.COMPATIBLE)
    ]
    assert _specifications(packages["tilde"]) == [
        ("1.2.3", DependencySpecifications.APPROX_EQ)
    ]
    assert _specifications(packages["hyphen"]) == [
        ("1.0.0", DependencySpecifications.GTE),
        ("2.0.0", DependencySpecifications.LTE),
    ]


def test_nodejs_partial_versions_are_x_ranges():
    # A partial version is an X-range in npm: `20` := `20.x.x`.
    packages = _parse_dependencies(
        {
            "major": "20",
            "minor": "20.1",
            "full": "20.1.0",
            "double-x": "2.x.x",
            "star": "1.2.*",
        }
    )

    assert _specifications(packages["major"]) == [
        ("20", DependencySpecifications.APPROX_EQ)
    ]
    assert _specifications(packages["minor"]) == [
        ("20.1", DependencySpecifications.APPROX_EQ)
    ]
    assert _specifications(packages["full"]) == [
        ("20.1.0", DependencySpecifications.EQ)
    ]
    assert _specifications(packages["double-x"]) == [
        ("2", DependencySpecifications.APPROX_EQ)
    ]
    assert _specifications(packages["star"]) == [
        ("1.2", DependencySpecifications.APPROX_EQ)
    ]


def test_nodejs_grading_partial_and_spaced_versions():
    packages = _parse_dependencies({"partial": "20", "spaced": ">= 1.2.3"})
    requirement = PackageRequirement(name="dep", warn="v21.0.0", block="v2.0.0")

    assert check_package(requirement, packages["partial"]) == PackageCheck.WARN
    assert check_package(requirement, packages["spaced"]) == PackageCheck.NOOP
