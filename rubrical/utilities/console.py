import rich
import typer


def print_header(message: str, emoji: str = "") -> None:
    rich.print(f"[bold dodger_blue1]{f'{emoji} '}{message}[/bold dodger_blue1]")


def print_message(message: str, emoji: str = "") -> None:
    rich.print(f"[steel_blue1]{f'{emoji} '}{message}[/steel_blue1]")


def print_raw(message: str, emoji: str = "") -> None:
    rich.print(f"{f'{emoji} '}{message}")


def print_debug(message: str) -> None:
    rich.print(f"Debug: {message}")


def print_error(message: str, emoji: str = "") -> None:
    rich.print(f"[bold bright_red]{f'{emoji} '}{message}[/bold bright_red]")
    raise typer.Exit(code=1)
