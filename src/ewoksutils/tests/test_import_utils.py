import os
import pytest
from .. import import_utils


def test_import_qualname(tmpdir):
    filename = tmpdir / "mymodule.py"
    with open(filename, "w") as f:
        f.write("class A:\n  pass")

    cwd = os.getcwd()
    os.chdir(str(tmpdir))
    try:
        import_utils.import_qualname("mymodule.A")

        with open(filename, "a") as f:
            f.write("\nclass B:\n  pass")

        with pytest.raises(ImportError):
            import_utils.import_qualname("mymodule.B")

        import_utils.import_qualname("mymodule.B", reload=True)

    finally:
        os.chdir(str(cwd))
