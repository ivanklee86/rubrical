from pathlib import Path

from typer.testing import CliRunner

from rubrical.main import app
from tests.constants import BASE_TEST_PATH

runner = CliRunner()


def test_cli_basic():
    result = runner.invoke(
        app,
        [
            "--config",
            str(Path(BASE_TEST_PATH, "files", "rubrical.yaml")),
            "--target",
            str(Path(BASE_TEST_PATH)),
        ],
    )
    assert result.exit_code == 1
    assert "update to" in result.stdout
