import pytest

from exceptiongroup import ExceptionGroup


def test_exception_group_init():
    memberA = ValueError("A")
    memberB = RuntimeError("B")
    group = ExceptionGroup(
        "many error.", [memberA, memberB], [str(memberA), str(memberB)]
    )
    assert group.exceptions == [memberA, memberB]
    assert group.message == "many error."
    assert group.sources == [str(memberA), str(memberB)]


def test_exception_group_when_members_are_not_exceptions():
    with pytest.raises(TypeError):
        ExceptionGroup(
            "error",
            [RuntimeError("RuntimeError"), "error2"],
            ["RuntimeError", "error2"],
        )


def test_exception_group_init_when_length_of_args_is_less_than_3():
    with pytest.raises(ValueError):
        ExceptionGroup("error")


def test_exception_group_init_when_exceptions_messages_not_equal():
    with pytest.raises(ValueError):
        ExceptionGroup(
            "many error.", [ValueError("A"), RuntimeError("B")], ["A"]
        )


def test_exception_group_str():
    memberA = ValueError("memberA")
    memberB = ValueError("memberB")
    group = ExceptionGroup(
        "many error.", [memberA, memberB], [str(memberA), str(memberB)]
    )
    assert "memberA" in str(group)
    assert "memberB" in str(group)

    assert "ExceptionGroup: " in repr(group)
    assert "memberA" in repr(group)
    assert "memberB" in repr(group)
