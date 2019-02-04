import _common

import exceptiongroup


def exc1_fn():
    try:
        raise ValueError
    except Exception as exc:
        return exc


def exc2_fn():
    try:
        raise KeyError
    except Exception as exc:
        return exc


# This should be printed nicely, because we overrode sys.excepthook
raise exceptiongroup.ExceptionGroup("demo", [exc1_fn(), exc2_fn()], ["a", "b"])
