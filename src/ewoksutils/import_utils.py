import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from typing import Callable
from typing import Type
from typing import TypeVar

T = TypeVar("T")


def qualname(obj: Any) -> str:
    """Return fully qualified name of a class or function (module + name)."""
    return obj.__module__ + "." + obj.__name__


def import_module(module_name: str, reload: bool = False) -> ModuleType:
    """Import a module given a qualified name or path.

    Supports:
      - module.submodule
      - /path/to/module/submodule.py

    If reload=True, reloads the module if already imported.
    """
    path = Path(module_name)
    if path.is_file() and path.suffix == ".py":
        mod_name = path.stem
        already_loaded = mod_name in sys.modules
        if already_loaded and not reload:
            mod = sys.modules[mod_name]
        else:
            spec = importlib.util.spec_from_file_location(mod_name, path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot import {module_name} as module")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
    else:
        already_loaded = module_name in sys.modules
        mod = importlib.import_module(module_name)
        if already_loaded and reload:
            mod = importlib.reload(mod)
    return mod


def import_qualname(name: str, reload: bool = False) -> Any:
    """Import an object by qualified name or path.

    Supports:
      - module_name.obj_name
      - /path/to/file.py::obj_name
    """
    if not isinstance(name, str):
        raise TypeError(name, type(name))

    if "::" in name:
        # path/to/file.py::ObjectName
        file_path, obj_name = name.rsplit("::", 1)
        module = import_module(file_path, reload=reload)
        try:
            return getattr(module, obj_name)
        except AttributeError:
            raise ImportError(f"Cannot import {obj_name} from {file_path}")
    else:
        module_name, _, obj_name = name.rpartition(".")
        if not module_name:
            raise ImportError(f"Cannot import {name}, no module part found")

        if "" not in sys.path:
            sys.path.insert(0, "")  # ensure current dir is in sys.path

        module = import_module(module_name, reload=reload)
        try:
            return getattr(module, obj_name)
        except AttributeError:
            raise ImportError(f"Cannot import {obj_name} from {module_name}")


def import_method(name: str, reload: bool = False) -> Callable:
    """Import a callable object by qualified name or path.

    Supports:
      - module_name.func_name
      - /path/to/file.py::func_name
    """
    method = import_qualname(name, reload=reload)
    if not callable(method):
        raise TypeError(f"{name!r} is not callable (got {type(method)})")
    return method


def instantiate_class(class_name: str, *args, **kwargs) -> T:
    """Instantiate a class given its qualified name or path.

    Supports:
      - module_name.ClassName
      - /path/to/file.py::ClassName
    """
    cls: Type[T] = import_qualname(class_name)
    if not isinstance(cls, type):
        raise TypeError(f"{class_name!r} is not a class (got {type(cls)})")
    return cls(*args, **kwargs)
