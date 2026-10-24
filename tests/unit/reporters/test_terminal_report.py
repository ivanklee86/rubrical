from rubrical.enum import PackageCheck
from rubrical.reporters import terminal
from rubrical.schemas.results import PackageCheckResult

SAMPLE_DATA = [
    PackageCheckResult("File1.json", "Dep1", PackageCheck.OK, "1.1.1", "", ""),
    PackageCheckResult(
        "File1.json", "Dep2", PackageCheck.WARN, "0.1.2", "0.1.3", "0.1.1"
    ),
    PackageCheckResult(
        "File2.json", "Dep3", PackageCheck.BLOCK, "1.1.1", "1.1.0", "1.1.2"
    ),
]


def test_terminal_report():
    terminal.terminal_report("Test Manager", SAMPLE_DATA)


def test_terminal_report_skips_noop(capsys):
    terminal.terminal_report(
        "Test Manager",
        [
            PackageCheckResult(
                name="NoopDep",
                file="File1.json",
                check=PackageCheck.NOOP,
                version_package=">1.0.0",
                version_block="1.1.0",
                version_warn="1.1.2",
            ),
            PackageCheckResult(
                name="BlockDep",
                file="File1.json",
                check=PackageCheck.BLOCK,
                version_package="1.0.0",
                version_block="1.1.0",
                version_warn="1.1.2",
            ),
        ],
    )

    output = capsys.readouterr().out
    assert "BlockDep" in output
    assert "NoopDep" not in output
