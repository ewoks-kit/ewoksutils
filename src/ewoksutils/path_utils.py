import os
from pathlib import Path
from typing import Union


def makedirs_from_filename(filename: Union[str, Path]):
    dirname = os.path.dirname(filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
