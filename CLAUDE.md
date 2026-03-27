# Claude.md - Rubrical Development Guidelines

This document outlines best practices for contributing to Rubrical, a CLI tool for dependency version management.

## Project Overview

Rubrical is a Python CLI tool that encourages developers to update their dependencies by checking version constraints across multiple package managers (Python, Node.js, Go, Jsonnet).

## Coding Style

### Import Ordering

Imports follow a strict order enforced by `ruff`:

1. Standard library imports
2. Third-party imports
3. Local imports

```python
# Standard library
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Third-party
from pydantic import BaseModel
from rich.console import Console
import typer

# Local
from rubrical.enum import PackageCheck, SupportedPackageManagers
from rubrical.schemas.configuration import RubricalConfig
```

### Naming Conventions

- **Classes**: PascalCase (`BasePackageManager`, `RubricalConfig`, `PackageCheckResult`)
- **Functions/methods**: snake_case (`check_package_managers`, `parse_package_manager_files`)
- **Private methods**: Leading underscore (`_parse_requirement`, `_parse_packagelock`)
- **Constants**: UPPER_SNAKE_CASE (`PACKAGE_MANAGER_MAPPING`, `TEST_CONFIG_BLOCK`)
- **Enums**: PascalCase class names, UPPER_SNAKE_CASE or lowercase values depending on usage

### Type Hints

All functions must have complete type annotations for parameters and return values:

```python
def check_package_managers(self) -> Tuple[bool, bool, Dict[str, List[PackageCheckResult]]]:
    warnings_found: bool = False
    blocks_found: bool = False
    results: Dict[str, List[PackageCheckResult]] = {}
    # ...
    return warnings_found, blocks_found, results

def match_from_specification_symbols(self, version: str) -> Tuple[DependencySpecifications, str]:
    # ...
```

Use `typing` module types: `Dict`, `List`, `Tuple`, `Optional`, etc.

### Docstrings

Keep docstrings concise and use triple double-quotes:

```python
@app.command()
def grade(...):
    """
    A CLI to encourage (😅) people to update their dependencies!
    """
```

For simple functions, single-line docstrings are acceptable:

```python
def validate(config: Path = typer.Option(...)):
    """Validates rubrical config."""
```

### Data Structures

#### Use `@dataclass` for simple data containers:

```python
from dataclasses import dataclass

@dataclass
class PackageManagerFileDetails:
    name: str
    path: Path
    contents: str

@dataclass
class Package:
    name: str
    raw_constraint: str
    version_constraints: List[Specification]
```

#### Use Pydantic `BaseModel` for validated configurations:

```python
from pydantic import BaseModel

class RubricalConfig(BaseModel):
    version: int
    blocking_mode: Optional[bool] = True
    package_managers: List[PackageManager]
```

### Enums

Use enums for type-safe constants:

```python
from enum import Enum

class PackageCheck(Enum):
    OK = "ok"
    WARN = "warn"
    BLOCK = "block"
    NOOP = "noop"

class SupportedPackageManagers(Enum):
    PYTHON = "python"
    NODEJS = "nodejs"
    GO = "go"
    JSONNET = "jsonnet"
```

### Abstract Base Classes

Use ABC for extensible components (package managers, reporters):

```python
import abc

class BasePackageManager(abc.ABC):
    @abc.abstractmethod
    def parse_package_manager_file(
        self, package_manager_file_details: PackageManagerFileDetails
    ) -> None:
        pass

    @abc.abstractmethod
    def read_package_manager_files(self, current_folder: Path) -> None:
        pass
```

Concrete implementations inherit and implement all abstract methods:

```python
class Python(BasePackageManager):
    def parse_package_manager_file(
        self, package_manager_file_details: PackageManagerFileDetails
    ) -> None:
        # Implementation
        pass
```

## Unit Test Style

### Test Organization

Tests mirror the package structure:

```
tests/
├── conftest.py            # Shared pytest configuration
├── fixtures.py            # Shared fixtures
├── constants.py           # Test constants
├── unit/
│   ├── comparisons/       # Tests for rubrical/comparisons/
│   ├── package_managers/  # Tests for rubrical/package_managers/
│   └── reporters/         # Tests for rubrical/reporters/
└── integration/
    └── test_cli.py        # End-to-end CLI tests
```

### Test Naming

- Test files: `test_<module>.py`
- Test functions: `test_<scenario>()` or `test_<class>_<method>()`

```python
def test_python():
    """Test Python package manager parsing."""

def test_poetry():
    """Test Poetry-specific parsing."""

def test_semver_eq():
    """Test semantic version equality comparison."""
```

### Designing Testable Classes

Classes should be designed for isolation:

1. **Accept dependencies as parameters** rather than creating them internally
2. **Separate file I/O from parsing logic**
3. **Use dataclasses for intermediate state** to make assertions easier

Example of testable design:

```python
class Python(BasePackageManager):
    def __init__(self):
        self.packages: Dict[str, List[Package]] = {}
        self.package_manager_file_details: List[PackageManagerFileDetails] = []

    def read_package_manager_files(self, current_folder: Path):
        # Reads files and stores in package_manager_file_details
        pass

    def parse_package_manager_files(self):
        # Parses stored file details into packages
        for file_details in self.package_manager_file_details:
            self.parse_package_manager_file(file_details)
```

This allows testing parsing in isolation:

```python
def test_python():
    python = Python()
    python.read_package_manager_files(Path(FILES_FOLDER_PATH, "python"))
    python.parse_package_manager_files()

    assert len(python.packages["requirements.txt"]) == 6
    [dep] = [x for x in python.packages["requirements.txt"] if x.name == "docopt"]
    assert dep.version_constraints[0].version == "0.6.1"
```

### Unit Test Patterns

#### Direct Object Testing

Create objects directly and verify state:

```python
def test_python():
    python = Python()
    python.read_package_manager_files(Path(FILES_FOLDER_PATH, "python"))
    python.parse_package_manager_files()

    assert len(python.packages["requirements.txt"]) == 6
    [dep] = [x for x in python.packages["requirements.txt"] if x.name == "docopt"]
    assert dep.version_constraints[0].version == "0.6.1"
    assert dep.version_constraints[0].specifier == DependencySpecifications.EQUAL
```

#### Testing Pure Functions

For comparison functions, test with various inputs:

```python
def test_semver_eq():
    result = compare_package_semver(
        PackageRequirement(name="test", warn="1.0.0", block="0.5.0", type=PackageTypes.SEMVER),
        Package(
            name="test",
            raw_constraint="==1.0.0",
            version_constraints=[Specification(specifier=DependencySpecifications.EQUAL, version="1.0.0")]
        )
    )
    assert result == PackageCheck.OK
```

#### Inline Test Data

Define test data inline using dictionaries:

```python
TEST_CONFIG_BLOCK = {
    "version": 1,
    "package_managers": [
        {
            "name": "jsonnet",
            "packages": [
                {"name": "xunleii/vector_jsonnet", "warn": "v0.1.3", "block": "v0.1.0"},
            ],
        }
    ],
}

def test_rubrical_config():
    config = RubricalConfig(**TEST_CONFIG_BLOCK)
    assert config.version == 1
```

#### Exception Testing

Use `pytest.raises()` for expected exceptions:

```python
import pytest
from typer import Exit

def test_print_error():
    with pytest.raises(Exit):
        console.print_error("Oops!")
```

## Integration Tests

### CLI Testing with Typer

Use `typer.testing.CliRunner` for end-to-end CLI tests:

```python
from typer.testing import CliRunner
from rubrical.main import app

runner = CliRunner()

def test_cli_basic():
    result = runner.invoke(
        app,
        [
            "grade",
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
            "--debug",
        ],
    )
    assert result.exit_code == 1
    assert "update to" in result.stdout
```

### Pytest Fixtures

Define reusable fixtures in `tests/fixtures.py`:

```python
import pytest
from dotenv import load_dotenv

@pytest.fixture
def secrets():
    """Load environment variables for tests requiring credentials."""
    load_dotenv()
    yield

@pytest.fixture
def github_pr_clean(secrets):
    """Provide a clean GitHub PR for testing."""
    g = Github(os.getenv("RUBRICAL_TEST_GITHUB_ACCESS_TOKEN"))
    repo = g.get_repo(GITHUB_REPO_NAME)
    pr = repo.get_pull(GITHUB_TEST_PR)

    # Cleanup before test
    for issue_comment in pr.get_issue_comments():
        issue_comment.delete()
        time.sleep(5)

    yield pr
```

### Mocking with pytest-mock

Use the `mocker` fixture from `pytest-mock` for mocking:

```python
def test_with_mock(mocker):
    # Mock a function
    mock_func = mocker.patch("rubrical.module.some_function")
    mock_func.return_value = "mocked_value"

    # Test code that calls some_function
    result = code_under_test()

    # Verify mock was called
    mock_func.assert_called_once_with(expected_arg)
```

### Mocking External Services

For GitHub API or other external services:

```python
def test_github_reporter(mocker):
    # Mock the GitHub client
    mock_github = mocker.patch("rubrical.reporters.gh.Github")
    mock_repo = mocker.MagicMock()
    mock_pr = mocker.MagicMock()

    mock_github.return_value.get_repo.return_value = mock_repo
    mock_repo.get_pull.return_value = mock_pr

    # Test the reporter
    reporter = GitHubReporter(token="fake", repo="owner/repo", pr_number=1)
    reporter.report(results)

    # Verify interactions
    mock_pr.create_issue_comment.assert_called_once()
```

### File System Mocking

Use `tmp_path` fixture for file system tests:

```python
def test_file_reading(tmp_path):
    # Create test file
    test_file = tmp_path / "requirements.txt"
    test_file.write_text("requests==2.28.0\nflask>=2.0.0")

    # Test reading
    python = Python()
    python.read_package_manager_files(tmp_path)
    python.parse_package_manager_files()

    assert len(python.packages["requirements.txt"]) == 2
```

### Test Data Files

Store complex test fixtures in `tests/files/`:

```
tests/
├── files/
│   ├── rubrical.yaml        # Test configuration
│   ├── python/
│   │   ├── requirements.txt
│   │   └── pyproject.toml
│   ├── nodejs/
│   │   └── package-lock.json
│   └── go/
│       └── go.mod
```

Reference in tests using constants:

```python
# tests/constants.py
from pathlib import Path

BASE_TEST_PATH = Path(__file__).parent
FILES_FOLDER_PATH = Path(BASE_TEST_PATH, "files")

# In tests
def test_python():
    python.read_package_manager_files(Path(FILES_FOLDER_PATH, "python"))
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rubrical

# Run specific test file
pytest tests/unit/package_managers/test_python.py

# Run in parallel
pytest -n auto
```

## Linting and Formatting

```bash
# Format code
ruff format .

# Check linting
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

## Pre-commit Hooks

Install pre-commit hooks before contributing:

```bash
pre-commit install
```

Hooks run automatically on commit:
- `trailing-whitespace`: Remove trailing whitespace
- `end-of-file-fixer`: Ensure files end with newline
- `check-yaml`: Validate YAML syntax
- `ruff-check`: Lint Python code
- `ruff-format`: Format Python code
- `uv-lock`: Keep uv.lock in sync
