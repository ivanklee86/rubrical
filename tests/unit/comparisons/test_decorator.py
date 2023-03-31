from rubrical.comparisons.decorator import results
from rubrical.enum import PackageCheck


@results
def silly_function():
    return (True, True)


def test_reporting_decorator():
    result = silly_function()
    assert result == PackageCheck.BLOCK
