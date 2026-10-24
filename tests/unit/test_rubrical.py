# ruff: noqa: PLR2004
from pathlib import Path

from rubrical.enum import PackageCheck
from rubrical.rubrical import Rubrical
from rubrical.schemas.configuration import RubricalConfig
from tests.constants import FILES_FOLDER_PATH

TEST_CONFIG_BLOCK = {
    "version": 1,
    "package_managers": [
        {
            "name": "jsonnet",
            "packages": [
                {"name": "xunleii/vector_jsonnet", "warn": "v0.1.3", "block": "v0.1.0"},
                {
                    "name": "jsonnet-libs/argo-workflows-libsonnet",
                    "warn": "v1.1.3",
                    "block": "v1.1.2",
                },
            ],
        }
    ],
}

TEST_CONFIG_WARNINGS = {
    "version": 1,
    "package_managers": [
        {
            "name": "jsonnet",
            "packages": [
                {"name": "xunleii/vector_jsonnet", "warn": "v0.1.3", "block": "v0.1.0"},
                {
                    "name": "jsonnet-libs/argo-workflows-libsonnet",
                    "warn": "v1.1.2",
                    "block": "v1.1.0",
                },
            ],
        }
    ],
}

TEST_CONFIG_CLEAN = {
    "version": 1,
    "package_managers": [
        {
            "name": "jsonnet",
            "packages": [
                {"name": "xunleii/vector_jsonnet", "warn": "v0.1.1", "block": "v0.1.0"},
                {
                    "name": "jsonnet-libs/argo-workflows-libsonnet",
                    "warn": "v1.1.0",
                    "block": "v1.0.1",
                },
            ],
        }
    ],
}


TEST_JSONNET_FOLDER = Path(FILES_FOLDER_PATH, "jsonnet")


def test_rubrical_single():
    test_config = RubricalConfig(**TEST_CONFIG_BLOCK)  # ty: ignore
    rubrical = Rubrical(test_config, TEST_JSONNET_FOLDER)
    result = rubrical.check_package_manager(rubrical.package_managers[0])

    assert len(result) == 2
    [dependency_one] = [x for x in result if x.name == "xunleii/vector_jsonnet"]
    assert dependency_one.check == PackageCheck.WARN
    [dependency_two] = [
        x for x in result if x.name == "jsonnet-libs/argo-workflows-libsonnet"
    ]
    assert dependency_two.check == PackageCheck.BLOCK


def test_rubrical_blocks():
    test_config = RubricalConfig(**TEST_CONFIG_BLOCK)  # ty: ignore
    rubrical = Rubrical(test_config, TEST_JSONNET_FOLDER)
    (warnings_found, blocks_found, check_results) = rubrical.check_package_managers()

    assert warnings_found
    assert blocks_found
    assert check_results


def test_rubrical_warnings():
    test_config = RubricalConfig(**TEST_CONFIG_WARNINGS)  # ty: ignore
    rubrical = Rubrical(test_config, TEST_JSONNET_FOLDER)
    (warnings_found, blocks_found, check_results) = rubrical.check_package_managers()

    assert warnings_found
    assert not blocks_found
    assert check_results


def test_rubrical_clean():
    test_config = RubricalConfig(**TEST_CONFIG_CLEAN)  # ty: ignore
    rubrical = Rubrical(test_config, TEST_JSONNET_FOLDER)
    (warnings_found, blocks_found, check_results) = rubrical.check_package_managers()

    assert not warnings_found
    assert not blocks_found
    assert check_results


def test_rubrical_python_name_normalization():
    test_config = RubricalConfig(
        **{
            "version": 1,
            "package_managers": [
                {
                    "name": "python",
                    "packages": [
                        {"name": "mopidy_dirble", "warn": "v1.2.2", "block": "v1.2.1"}
                    ],
                }
            ],
        }
    )
    rubrical = Rubrical(test_config, Path(FILES_FOLDER_PATH, "python"))
    result = rubrical.check_package_manager(rubrical.package_managers[0])

    [dependency] = result
    assert dependency.name == "Mopidy-Dirble"
    assert dependency.check == PackageCheck.BLOCK


def test_rubrical_nodejs_name_not_normalized():
    test_config = RubricalConfig(
        **{
            "version": 1,
            "package_managers": [
                {
                    "name": "nodejs",
                    "packages": [
                        {"name": "React", "warn": "v17.0.4", "block": "v17.0.3"}
                    ],
                }
            ],
        }
    )
    rubrical = Rubrical(test_config, Path(FILES_FOLDER_PATH, "nodejs"))
    result = rubrical.check_package_manager(rubrical.package_managers[0])

    assert not result


TEST_CONFIG_LANGUAGES = {
    "version": 1,
    "languages": [
        {"name": "python", "warn": "v3.12.0", "block": "v3.10.0"},
        {"name": "go", "warn": "v1.22.0", "block": "v1.20.0"},
        {"name": "nodejs", "warn": "v20.0.0", "block": "v18.17.0"},
    ],
}


def test_rubrical_languages():
    test_config = RubricalConfig(**TEST_CONFIG_LANGUAGES)  # ty: ignore
    rubrical = Rubrical(test_config, FILES_FOLDER_PATH)
    (warnings_found, blocks_found, check_results) = rubrical.check_all()

    assert warnings_found
    assert blocks_found
    assert list(check_results.keys()) == ["languages"]
    assert {(x.name, x.file): x.check for x in check_results["languages"]} == {
        ("python", "python/pyproject.toml"): PackageCheck.BLOCK,
        ("python", "python-gt/pyproject.toml"): PackageCheck.BLOCK,
        ("python", "poetry-or/pyproject.toml"): PackageCheck.BLOCK,
        ("python", "uv/pyproject.toml"): PackageCheck.OK,
        ("python", "poetry/pyproject.toml"): PackageCheck.OK,
        ("go", "go/go.mod"): PackageCheck.BLOCK,
        ("go", "go-implicit/go.mod"): PackageCheck.BLOCK,
        ("go", "go-toolchain/go.mod"): PackageCheck.WARN,
        ("nodejs", "nodejs/engines/minimum/package.json"): PackageCheck.BLOCK,
        ("nodejs", "nodejs/engines/range/package.json"): PackageCheck.WARN,
        ("nodejs", "nodejs/engines/or-range/package.json"): PackageCheck.WARN,
        ("nodejs", "nodejs/engines/partial-gt/package.json"): PackageCheck.WARN,
        ("nodejs", "nodejs/engines/spaced/package.json"): PackageCheck.WARN,
        ("nodejs", "nodejs/engines/caret/package.json"): PackageCheck.OK,
        ("nodejs", "nodejs/engines/wildcard/package.json"): PackageCheck.OK,
        ("nodejs", "nodejs/engines/any/package.json"): PackageCheck.NOOP,
        ("python", "version-files/python/.python-version"): PackageCheck.OK,
        ("python", "version-files/python-multi/.python-version"): PackageCheck.BLOCK,
        ("python", "version-files/python-specifier/.python-version"): (
            PackageCheck.WARN
        ),
        ("python", "version-files/python-pypy/.python-version"): PackageCheck.NOOP,
        ("python", "version-files/python-system/.python-version"): PackageCheck.NOOP,
        ("go", "version-files/go/.go-version"): PackageCheck.WARN,
        ("nodejs", "version-files/node/.node-version"): PackageCheck.WARN,
        ("nodejs", "version-files/nvmrc/.nvmrc"): PackageCheck.OK,
        ("nodejs", "version-files/nvmrc-lts/.nvmrc"): PackageCheck.NOOP,
    }


def test_rubrical_languages_report_declaration_and_thresholds():
    test_config = RubricalConfig(**TEST_CONFIG_LANGUAGES)  # ty: ignore
    rubrical = Rubrical(test_config, Path(FILES_FOLDER_PATH, "go"))
    [result] = rubrical.check_languages()

    assert result.file == "go.mod"
    assert result.version_package == "go 1.19"
    assert result.version_warn == "v1.22.0"
    assert result.version_block == "v1.20.0"


def test_rubrical_languages_and_package_managers():
    test_config = RubricalConfig(
        **TEST_CONFIG_WARNINGS,  # ty: ignore
        languages=[{"name": "go", "warn": "v1.0.0", "block": "v1.0.0"}],
    )
    rubrical = Rubrical(test_config, FILES_FOLDER_PATH)
    (warnings_found, blocks_found, check_results) = rubrical.check_all()

    # Package manager warnings still surface when languages are clean.
    assert warnings_found
    assert not blocks_found
    assert list(check_results.keys()) == ["languages", "jsonnet"]
    assert all(x.check == PackageCheck.OK for x in check_results["languages"])


def test_rubrical_without_languages_reports_only_package_managers():
    test_config = RubricalConfig(**TEST_CONFIG_BLOCK)  # ty: ignore
    rubrical = Rubrical(test_config, TEST_JSONNET_FOLDER)
    (_, _, check_results) = rubrical.check_all()

    assert list(check_results.keys()) == ["jsonnet"]
