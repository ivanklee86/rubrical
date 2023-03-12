from typing import List

from rich.console import Console
from rich.table import Table

from rubrical.enum import PackageCheck
from rubrical.rubrical import PackageCheckResult
from rubrical.utilities import terminal


def terminal_report(
    package_manager_name: str, check_results: List[PackageCheckResult]
) -> None:
    console = Console()

    terminal.print_message(f"Result for {package_manager_name}")

    table = Table("File", "Dependency", "Result")
    for result in check_results:
        if result.check == PackageCheck.BLOCK:
            result_text = f"❌ {result.version_package} <= {result.version_block}, update to > {result.version_warn}"
        elif result.check == PackageCheck.WARN:
            result_text = f"⚠️ {result.version_package} <= {result.version_warn}"
        else:
            result_text = "✅"

        table.add_row(result.file, result.name, result_text)

    console.print(table)
