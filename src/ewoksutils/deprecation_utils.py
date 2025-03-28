import sys
import warnings

if sys.version_info < (3, 13):

    from functools import wraps

    def deprecated(message: str):
        def decorator(deprecated_fn):
            @wraps(deprecated_fn)
            def wrapper(*a, **k):
                warnings.warn(message, DeprecationWarning, stacklevel=2)
                return deprecated_fn(*a, **k)

            return wrapper

        return decorator

else:
    deprecated = warnings.deprecated
