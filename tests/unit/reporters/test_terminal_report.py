from rubrical.enum import PackageCheck
from rubrical.reporters import terminal
from rubrical.rubrical import PackageCheckResult

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
