import pytest
from click.exceptions import Exit

from rubrical.utilities import console


def test_print():
    console.print_header("This is a header!")
    console.print_message("This is a message!")
    console.print_raw("[bold]Nothing to see here[/bold]")
    with pytest.raises(Exit):
        console.print_error("Oops!")
