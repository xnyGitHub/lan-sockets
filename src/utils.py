"""Util class"""

def flush_print_default(func):
    """Print flush decorator for MINGW64"""
    printer = func

    def wrapped(*args):
        printer(*args, flush=True)

    return wrapped

# pylint: disable=unused-argument
def ctrlc_handler(signum, frame):

    """Crtl+Z handler for mac"""
    print("Ctrl+Z pressed, but ignored, use Ctrl+C instead")
