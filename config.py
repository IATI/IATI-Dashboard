"""These functions join path fragments to make directories to different input or output files

Note: eventually these functions will probably become redundant or refactored into
a different module, but for now this helps in refactoring the code.
"""

import os.path


STATS_DIRECTORY = "./stats-calculated"
DATA_DIRECTORY = "./data"
BASE_DIRECTORY = "./"
OUT_DIRECTORY = "./out"


def join_stats_path(p: str) -> str:
    """Make a path to a file or directory within the downloaded stats directory
    """
    return os.path.join(STATS_DIRECTORY, p)


def join_data_path(p: str) -> str:
    """Make a path to a file or directory within the downloaded data directory
    """
    return os.path.join(DATA_DIRECTORY, p)


def join_base_path(p: str) -> str:
    """Make a path to a file or directory relative to the base of the dashboard directory
    """
    return os.path.join(BASE_DIRECTORY, p)


def join_out_path(p: str) -> str:
    """Make a path to a file or directory relative to the base of the out directory
    """
    return os.path.join(OUT_DIRECTORY, p)
