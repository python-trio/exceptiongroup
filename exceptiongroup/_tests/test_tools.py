from exceptiongroup import ExceptionGroup, split, catch


def test_split_for_none_exception():
    matched, unmatched = split(RuntimeError, None)
    assert matched is None
    assert unmatched is None


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
        ['Runtime Error1', 'Value Error2']
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
        ['skip', 'Runtime Error']
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
