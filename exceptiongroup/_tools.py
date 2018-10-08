################################################################
# Core primitives for working with ExceptionGroups
################################################################

from . import ExceptionGroup

def split(exc_type, exc, *, match=None):
    if exc is None:
        return None, None
    elif isinstance(exc, ExceptionGroup):
        matches = []
        match_notes = []
        rests = []
        rest_notes = []
        for subexc, note in zip(exc.exceptions, exc.sources):
            match, rest = ExceptionGroup.split(exc_type, subexc, match=match)
            if match is not None:
                matches.append(match)
                match_notes.append(note)
            if rest is not None:
                rests.append(rest)
                rest_notes.append(note)
        if matches and not rests:
            return exc, None
        elif rests and not matches:
            return None, exc
        else:
            match = copy.copy(exc)
            match.exceptions = matches
            match.sources = match_notes
            rest = copy.copy(exc)
            rest.exceptions = rests
            rest.sources = rest_notes
            return match, rest
    else:
        if isinstance(exc, exc_type) and (match is None or match(exc)):
            return exc, None
        else:
            return None, exc


class Catcher:
    def __init__(self, exc_type, handler, match):
        self._exc_type = exc_type
        self._handler = handler
        self._match = match

    def __enter__(self):
        pass

    # Cases to think about:
    #
    # except RuntimeError:
    #     pass
    #
    # -> raise 'rest' if any, it gets one extra tb entry
    #
    # except RuntimeError as exc:
    #     raise OtherError
    #
    # -> set __context__ on OtherError, raise (OtherError, rest)
    #    obviously gets one extra tb entry, unavoidable. doesn't really matter
    #    whether rest exists.
    #
    # except RuntimeError as exc:
    #     raise
    # except RuntimeError as exc:
    #     raise exc
    #
    # -> in regular Python these are different. ('raise' resets the
    # __traceback__ to whatever it was when it was caught, and leaves
    # __context__ alone; 'raise exc' treats 'exc' like a new exception and
    # triggers that processing.) We can't realistically tell the difference
    # between these two cases, so we treat them both like 'raise'.
    # Specifically, if handler re-raises then we clear all context and tb
    # changes and then let the original exception propagate.
    #
    # Weird language semantics to watch out for:
    # If __exit__ returns False, then exc is reraised, *after restoring its
    # traceback to whatever it was on entry*. I think.
    #
    # And bare 'raise' restores the traceback to whatever was in
    # sys.exc_info()[2] when the exception was caught. I think. (This is why
    # we restore caught.__traceback__ *after* the handler runs, because
    # otherwise it might reset the tb back to a mangled state.)
    def __exit__(self, etype, exc, tb):
        __traceback_hide__ = True  # for pytest
        caught, rest = split(self._exc_type, exc, match=self._match)
        if caught is None:
            return False
        # 'raise caught' might mangle some of caught's attributes, and then
        # handler() might mangle them more. So we save and restore them.
        saved_caught_context = caught.__context__
        saved_caught_traceback = caught.__traceback__
        # Arrange that inside the handler, any new exceptions will get
        # 'caught' as their __context__, and bare 'raise' will work.
        try:
            raise caught
        except type(caught):
            try:
                self._handler(caught)
            except BaseException as handler_exc:
                if handler_exc is caught:
                    return False
                if rest is None:
                    exceptiongroup_catch_exc = handler_exc
                else:
                    exceptiongroup_catch_exc = ExceptionGroup(
                        "caught {}".format(
                            self._exc_type.__class__.__name__
                        ),
                        [handler_exc, rest],
                        ["exception raised by handler", "uncaught exceptions"]
                    )
            else:
                exceptiongroup_catch_exc = rest
            finally:
                caught.__context__ = saved_caught_context
                caught.__traceback__ = saved_caught_traceback

        # The 'raise' line here is arcane plumbling that regular end users
        # will see in the middle of tracebacks, so we try to make it readable
        # out-of-context.
        saved_context = exceptiongroup_catch_exc.__context__
        try:
            raise exceptiongroup_catch_exc
        finally:
            exceptiongroup_catch_exc.__context__ = saved_context


def catch(cls, exc_type, handler, match=None):
    return Catcher(exc_type, handler, match)
