from typer.testing import CliRunner

from rubrical.main import app

runner = CliRunner()


def test_cli_basic():
    result = runner.invoke(app, ["Bob"])
    assert not result.exit_code
    assert "Hello Bob" in result.stdout
