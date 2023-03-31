import functools
from typing import Callable

from rubrical.enum import PackageCheck


def results(func: Callable) -> PackageCheck:
    """
    Decorator to standarize reporting between multiple check strategies.
    """

    @functools.wraps(func)
    def results_wrapper(*args, **kwargs) -> PackageCheck:
        (warn_signal, block_signal) = func(*args, **kwargs)

        if block_signal:
            status = PackageCheck.BLOCK
        elif warn_signal:
            status = PackageCheck.WARN
        else:
            status = PackageCheck.OK

        return status

    return results_wrapper  # type: ignore
