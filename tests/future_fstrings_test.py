# -*- coding: future_fstrings -*-
import imp

import pytest

import future_fstrings


def test_hello_world():
    thing = 'world'
    assert f'hello {thing}' == 'hello world'


def test_maths():
    assert f'{5 + 5}' == '10'


def test_with_bangs():
    thing = 'world'
    assert f'hello {thing.replace("d", "d!")}' == 'hello world!'
    assert f'hello {1 != 2}' == 'hello True'


def test_with_braces():
    assert f'hello {{ hi }}' == 'hello { hi }'


def test_strings_quoting_variables():
    assert f'hello {"{x}"}' == 'hello {x}'
    assert f"hello {'{x}'}" == 'hello {x}'
    assert f'hello {"""{x}"""}' == 'hello {x}'
    assert f"hello {'''{x}'''}" == 'hello {x}'
    assert f'hello {"""a"a"""}' == 'hello a"a'


def test_sequence_literals():
    assert f'hello {[1, 2, 3][0]}' == 'hello 1'
    assert f'hello {sorted({1, 2, 3})[0]}' == 'hello 1'
    assert f'hello {(1, 2, 3)[0]}' == 'hello 1'


def test_nested_format_literals():
    x = 5
    y = 6
    fmt = '6d'
    assert f'{x:{y}d}' == '     5'
    assert f'{x:{fmt}}' == '     5'


def test_conversion_modifiers():
    assert f'hello {str("hi")!r}' == "hello 'hi'"


def _assert_fails_with_msg(s, expected_msg):
    with pytest.raises(AssertionError) as excinfo:
        future_fstrings._fstring_reformat(s)
    msg, = excinfo.value.args
    assert msg == expected_msg


def test_error_only_one_closing_paren():
    _assert_fails_with_msg("'hi }'", "f-string: single '}' is not allowed")


def test_error_unterminated_brace():
    _assert_fails_with_msg("'hi {'", "f-string: expecting '}'")


def test_error_backslash():
    _assert_fails_with_msg(
        r"""'hi {"\\"}'""",
        'f-string expression part cannot include a backslash',
    )


def test_error_contains_comment_character():
    _assert_fails_with_msg(
        "'hi {#}'", "f-string expression cannot include '#'",
    )


def test_unterminated_quotes():
    _assert_fails_with_msg("""'hi {"s""", 'f-string: unterminated string')


def test_incorrectly_nested_braces():
    _assert_fails_with_msg(
        "'hi {[1, 2'", "f-string: mismatched '(', '{', or '['",
    )


def test_too_deep():
    _assert_fails_with_msg(
        "'{x:{y:{z}}}'", 'f-string: expressions nested too deeply',
    )


def test_fix_coverage():
    """Because our module is loaded so early in python startup, coverage
    doesn't have a chance to instrument the module-level scope.

    Run this last so it doesn't interfere with tests in any way.
    """
    imp.reload(future_fstrings)
