import pytest

from ..deprecation_utils import deprecated


@deprecated("This function is deprecated")
def _deprecated_function():
    pass


class _TestClass:
    @deprecated("This method is deprecated")
    def deprecated_method(self):
        pass

    @property
    @deprecated("This property is deprecated")
    def deprecated_property(self):
        pass

    @classmethod
    @deprecated("This class method is deprecated")
    def deprecated_classmethod(cls):
        pass


def test_deprecated():
    with pytest.warns(DeprecationWarning):
        _deprecated_function()

    with pytest.warns(DeprecationWarning):
        _TestClass.deprecated_classmethod()

    instance = _TestClass()

    with pytest.warns(DeprecationWarning):
        instance.deprecated_method()

    with pytest.warns(DeprecationWarning):
        instance.deprecated_property
