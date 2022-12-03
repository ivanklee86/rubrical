import pytest
from click.exceptions import Exit

from rubrical.utilities import terminal


def test_print():
    terminal.print_header("This is a header!")
    terminal.print_message("This is a message!")
    terminal.print_raw("[bold]Nothing to see here[/bold]")
    with pytest.raises(Exit):
        terminal.print_error("Oops!")
