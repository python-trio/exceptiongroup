import pytest
from exceptiongroup import ExceptionGroup, split


def raise_error(err):
    raise err


def raise_error_from_another(out_err, another_err):
    # use try..except approache so out_error have meaningful
    # __context__, __cause__ attribute.
    try:
        raise another_err
    except Exception as e:
        raise out_err from e


def test_split_for_none_exception_should_raise_value_error():
    with pytest.raises(ValueError):
        matched, unmatched = split(RuntimeError, None)


def test_split_when_all_exception_matched():
    group = ExceptionGroup(
        "Many Errors",
        [RuntimeError("Runtime Error1"), RuntimeError("Runtime Error2")],
        ["Runtime Error1", "Runtime Error2"]
    )
    matched, unmatched = split(RuntimeError, group)
    assert matched is group
    assert unmatched is None


def test_split_when_all_exception_unmatched():
    group = ExceptionGroup(
        "Many Errors",
        [RuntimeError("Runtime Error1"), RuntimeError("Runtime Error2")],
        ["Runtime Error1", "Runtime Error2"]
    )
    matched, unmatched = split(ValueError, group)
    assert matched is None
    assert unmatched is group


def test_split_when_contains_matched_and_unmatched():
    error1 = RuntimeError("Runtime Error1")
    error2 = ValueError("Value Error2")
    group = ExceptionGroup(
        "Many Errors",
        [error1, error2],
        ["Runtime Error1", "Value Error2"]
    )
    matched, unmatched = split(RuntimeError, group)
    assert isinstance(matched, ExceptionGroup)
    assert isinstance(unmatched, ExceptionGroup)
    assert matched.exceptions == [error1]
    assert matched.message == "Many Errors"
    assert matched.sources == ['Runtime Error1']
    assert unmatched.exceptions == [error2]
    assert unmatched.message == "Many Errors"
    assert unmatched.sources == ['Value Error2']


def test_split_with_predicate():
    def _match(err):
        return str(err) != 'skip'

    error1 = RuntimeError("skip")
    error2 = RuntimeError("Runtime Error")
    group = ExceptionGroup(
        "Many Errors",
        [error1, error2],
        ["skip", "Runtime Error"]
    )
    matched, unmatched = split(RuntimeError, group, match=_match)
    assert matched.exceptions == [error2]
    assert unmatched.exceptions == [error1]


def test_split_with_single_exception():
    err = RuntimeError("Error")
    matched, unmatched = split(RuntimeError, err)
    assert matched is err
    assert unmatched is None

    matched, unmatched = split(ValueError, err)
    assert matched is None
    assert unmatched is err


def test_split_and_check_attributes_same():
    try:
        raise_error(RuntimeError("RuntimeError"))
    except Exception as e:
        run_error = e

    try:
        raise_error(ValueError("ValueError"))
    except Exception as e:
        val_error = e

    group = ExceptionGroup(
        "ErrorGroup", [run_error, val_error], ["RuntimeError", "ValueError"]
    )
    # go and check __traceback__, __cause__ attributes
    try:
        raise_error_from_another(group, RuntimeError("Cause"))
    except BaseException as e:
        new_group = e

    matched, unmatched = split(RuntimeError, group)
    assert matched.__traceback__ is new_group.__traceback__
    assert matched.__cause__ is new_group.__cause__
    assert matched.__context__ is new_group.__context__
    assert unmatched.__traceback__ is new_group.__traceback__
    assert unmatched.__cause__ is new_group.__cause__
    assert unmatched.__context__ is new_group.__context__
