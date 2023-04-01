from rubrical.enum import PackageCheck


def results_to_status(warn_signal: bool, block_signal: bool) -> PackageCheck:
    if block_signal:
        status = PackageCheck.BLOCK
    elif warn_signal:
        status = PackageCheck.WARN
    else:
        status = PackageCheck.OK

    return status
