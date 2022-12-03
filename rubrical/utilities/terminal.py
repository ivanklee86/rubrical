import rich
import typer


def print_header(message: str) -> None:
    rich.print(f"[bold dodger_blue1]{message}[/bold dodger_blue1]")


def print_message(message: str) -> None:
    rich.print(f"[bold steel_blue1]{message}[/bold steel_blue1]")


def print_raw(message: str) -> None:
    rich.print(message)


def print_error(message: str) -> None:
    rich.print(f"[bold bright_red]{message}[/bold bright_red]")
    raise typer.Exit(code=1)
