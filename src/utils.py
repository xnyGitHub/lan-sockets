"""Util class"""
from types import FrameType
from typing import Callable, Type
import sys


def flush_print_default(func: Callable) -> Callable:
    """Print flush decorator for MINGW64"""
    printer = func

    def wrapped(*args: str) -> None:
        printer(*args, flush=True)

    return wrapped


def socket_recv_errors(func: Callable) -> Callable:
    """Wrapper for common socket errors"""
    socket = func

    def wrapped(instance: Type, buffer_size: int) -> None:
        try:
            return socket(instance, buffer_size)
        except ConnectionAbortedError:
            print("The server is no longer online\nThe client will now exit")
            sys.exit(0)

    return wrapped


# pylint: disable=unused-argument
def ctrlc_handler(signum: int, frame: FrameType) -> None:

    """Crtl+Z handler for mac"""
    print("Ctrl+Z pressed, but ignored, use Ctrl+C instead")


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated: Type) -> None:
        self._decorated = decorated

    def instance(self) -> object:
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance: object = self._decorated()
            return self._instance

    def __call__(self) -> None:
        raise TypeError("Singletons must be accessed through `instance()`.")

    def __instancecheck__(self, inst: object) -> bool:
        return isinstance(inst, self._decorated)
