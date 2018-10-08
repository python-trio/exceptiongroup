import _common

import sys


def custom_excepthook(*args):
    print("custom running!")
    return sys.__excepthook__(*args)


sys.excepthook = custom_excepthook

# Should warn that we'll get kinda-broken tracebacks
import exceptiongroup

# The custom excepthook should run, because we were polite and didn't
# override it
raise exceptiongroup.ExceptionGroup(
    "demo", [ValueError(), KeyError()], ["a", "b"]
)
