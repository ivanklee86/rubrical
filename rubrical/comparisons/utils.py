from typing import List

from rubrical.enum import PackageCheck


def results_to_status(warn_signal: bool, block_signal: bool) -> PackageCheck:
    if block_signal:
        status = PackageCheck.BLOCK
    elif warn_signal:
        status = PackageCheck.WARN
    else:
        status = PackageCheck.OK

    return status


def max_status(results: List[PackageCheck]):
    for value in [
        PackageCheck.BLOCK,
        PackageCheck.WARN,
        PackageCheck.OK,
        PackageCheck.NOOP,
    ]:
        if value in results:
            return value
