import os

import pytest

from .. import import_utils


def test_import_qualname(tmp_path):
    filename = tmp_path / "mymodule1.py"
    with open(filename, "w") as f:
        f.write("class A:\n  pass")

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        import_utils.import_qualname("mymodule1.A")

        with open(filename, "a") as f:
            f.write("\nclass B:\n  pass")

        with pytest.raises(ImportError):
            import_utils.import_qualname("mymodule1.B")

        import_utils.import_qualname("mymodule1.B", reload=True)

    finally:
        os.chdir(str(cwd))


def test_import_qualname_path(tmp_path):
    filename = tmp_path / "mymodule2.py"
    with open(filename, "w") as f:
        f.write("class A:\n  pass")

    import_utils.import_qualname(f"{filename}::A")

    with open(filename, "a") as f:
        f.write("\nclass B:\n  pass")

    with pytest.raises(ImportError):
        import_utils.import_qualname(f"{filename}::B")

    import_utils.import_qualname(f"{filename}::B", reload=True)
