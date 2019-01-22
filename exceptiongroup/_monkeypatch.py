################################################################
# ExceptionGroup traceback formatting
#
# This file contains the terrible, terrible monkey patching of various things,
# especially the traceback module, to add support for handling
# ExceptionGroups.
################################################################

import sys
import textwrap
import traceback
import warnings

from . import ExceptionGroup

traceback_exception_original_init = traceback.TracebackException.__init__


def traceback_exception_init(
    self,
    exc_type,
    exc_value,
    exc_traceback,
    *,
    limit=None,
    lookup_lines=True,
    capture_locals=False,
    _seen=None
):
    if _seen is None:
        _seen = set()

    # Capture the original exception and its cause and context as
    # TracebackExceptions
    traceback_exception_original_init(
        self,
        exc_type,
        exc_value,
        exc_traceback,
        limit=limit,
        lookup_lines=lookup_lines,
        capture_locals=capture_locals,
        _seen=_seen,
    )

    # Capture each of the exceptions in the ExceptionGroup along with each of
    # their causes and contexts
    if isinstance(exc_value, ExceptionGroup):
        exceptions = []
        sources = []
        for exc, source in zip(exc_value.exceptions, exc_value.sources):
            if exc not in _seen:
                exceptions.append(
                    traceback.TracebackException.from_exception(
                        exc,
                        limit=limit,
                        lookup_lines=lookup_lines,
                        capture_locals=capture_locals,
                        # copy the set of _seen exceptions so that duplicates
                        # shared between sub-exceptions are not omitted
                        _seen=set(_seen),
                    )
                )
                sources.append(source)
        self.exceptions = exceptions
        self.sources = sources
    else:
        self.exceptions = []
        self.sources = []


def traceback_exception_format(self, *, chain=True):
    yield from traceback_exception_original_format(self, chain=chain)

    for exc, source in zip(self.exceptions, self.sources):
        yield "\n  {}:\n\n".format(source)
        yield from (textwrap.indent(line, " " * 4) for line in exc.format(chain=chain))


def exceptiongroup_excepthook(etype, value, tb):
    sys.stderr.write("".join(traceback.format_exception(etype, value, tb)))


traceback.TracebackException.__init__ = traceback_exception_init
traceback_exception_original_format = traceback.TracebackException.format
traceback.TracebackException.format = traceback_exception_format

IPython_handler_installed = False
warning_given = False
if "IPython" in sys.modules:
    import IPython

    ip = IPython.get_ipython()
    if ip is not None:
        if ip.custom_exceptions != ():
            warnings.warn(
                "IPython detected, but you already have a custom exception "
                "handler installed. I'll skip installing exceptiongroup's "
                "custom handler, but this means you won't see full tracebacks "
                "for ExceptionGroups.",
                category=RuntimeWarning,
            )
            warning_given = True
        else:

            def trio_show_traceback(self, etype, value, tb, tb_offset=None):
                # XX it would be better to integrate with IPython's fancy
                # exception formatting stuff (and not ignore tb_offset)
                exceptiongroup_excepthook(etype, value, tb)

            ip.set_custom_exc((ExceptionGroup,), trio_show_traceback)
            IPython_handler_installed = True

if sys.excepthook is sys.__excepthook__:
    sys.excepthook = exceptiongroup_excepthook
else:
    if not IPython_handler_installed and not warning_given:
        warnings.warn(
            "You seem to already have a custom sys.excepthook handler "
            "installed. I'll skip installing exceptiongroup's custom handler, "
            "but this means you won't see full tracebacks for "
            "ExceptionGroups.",
            category=RuntimeWarning,
        )
