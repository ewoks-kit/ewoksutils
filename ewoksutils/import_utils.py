import importlib


def qualname(obj):
    return obj.__module__ + "." + obj.__name__


def import_qualname(qualname):
    if not isinstance(qualname, str):
        raise TypeError(qualname, type(qualname))
    module_name, dot, obj_name = qualname.rpartition(".")
    if not module_name:
        raise ImportError(f"cannot import {qualname}")
    module = importlib.import_module(module_name)
    try:
        return getattr(module, obj_name)
    except AttributeError:
        raise ImportError(f"cannot import {obj_name} from {module_name}")


def import_method(qualname):
    method = import_qualname(qualname)
    if not callable(method):
        raise RuntimeError(repr(qualname) + " is not callable")
    return method


def instantiate_class(class_name: str, *args, **kwargs):
    cls = import_qualname(class_name)
    return cls(*args, **kwargs)
