from typing import List

from rich.console import Console
from rich.table import Table

from rubrical.enum import PackageCheck
from rubrical.schemas.results import PackageCheckResult
from rubrical.utilities import console


def terminal_report(
    package_manager_name: str, check_results: List[PackageCheckResult]
) -> None:
    # If any unsuccessful checks.
    if [x for x in check_results if x.check in [PackageCheck.BLOCK, PackageCheck.WARN]]:
        console.print_message(
            f"[bold][dark_orange]{package_manager_name}[/dark_orange][/bold] checks completed with violations!"
        )

        rconsole = Console()

        table = Table("File", "Dependency", "Result")

        # Only report unsuccessful checks.
        for result in [x for x in check_results if x.check != PackageCheck.OK]:
            if result.check == PackageCheck.BLOCK:
                result_text = f"❌ {result.version_package} <= {result.version_block}, update to > {result.version_warn}"
            elif result.check == PackageCheck.WARN:
                # Terminal is cranky about the emoji, needs two spaces.
                result_text = f"⚠️  {result.version_package} <= {result.version_warn}"

            table.add_row(result.file, result.name, result_text)

        rconsole.print(table)
    else:
        console.print_message(
            f"[bold][spring_green1]{package_manager_name}[/spring_green1][/bold] checks completed with no warnings or blocks!"
        )
