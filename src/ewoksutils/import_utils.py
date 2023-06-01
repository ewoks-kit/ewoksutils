import sys
import importlib
from types import ModuleType
from typing import Type, Callable, Any


def qualname(obj):
    return obj.__module__ + "." + obj.__name__


def import_module(module_name: str, reload: bool = False) -> ModuleType:
    already_loaded = module_name in sys.modules
    mod = importlib.import_module(module_name)
    if already_loaded and reload:
        return importlib.reload(mod)
    return mod


def import_qualname(qualname, reload: bool = False) -> Any:
    if not isinstance(qualname, str):
        raise TypeError(qualname, type(qualname))
    module_name, _, obj_name = qualname.rpartition(".")
    if not module_name:
        raise ImportError(f"cannot import {qualname}")

    if "" not in sys.path:
        # This happens when the python process was launched
        # through a python console script
        sys.path.append("")

    module = import_module(module_name, reload=reload)

    try:
        return getattr(module, obj_name)
    except AttributeError:
        raise ImportError(f"cannot import {obj_name} from {module_name}")


def import_method(qualname, reload: bool = False) -> Callable:
    method = import_qualname(qualname, reload=reload)
    if not callable(method):
        raise RuntimeError(repr(qualname) + " is not callable")
    return method


def instantiate_class(class_name: str, *args, **kwargs) -> Type:
    cls = import_qualname(class_name)
    return cls(*args, **kwargs)
