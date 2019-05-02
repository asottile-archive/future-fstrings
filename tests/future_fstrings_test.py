# -*- coding: future_fstrings -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import imp
import io
import subprocess
import sys

import pytest

import future_fstrings


xfailif_native = pytest.mark.xfail(
    future_fstrings.SUPPORTS_FSTRINGS, reason='natively supports fstrings',
)


def test_hello_world():
    thing = 'world'
    assert f'hello {thing}' == 'hello world'


def test_maths():
    assert f'{5 + 5}' == '10'


def test_long_unicode(tmpdir):
    # This only reproduces outside pytest
    f = tmpdir.join('f.py')
    f.write_text(
        '# -*- coding: future_fstrings -*-\n'
        'def test(a):\n'
        '    f"ЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙЙ {a}"\n'
        'test(1)\n',
        encoding='UTF-8',
    )
    assert not subprocess.check_output((sys.executable, f.strpath))


def test_very_large_file(tmpdir):
    # This only reproduces outside pytest.  See #23
    f = tmpdir.join('f.py')
    f.write(''.join((
        '# -*- coding: future_fstrings -*-\n'
        'def f(x): pass\n'
        'f(\n',
        '    "hi"\n' * 8192,
        ')\n',
    )))
    assert not subprocess.check_output((sys.executable, f.strpath))


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
    assert f"""hello {'''hi '" hello'''}""" == 'hello hi \'" hello'


def test_raw_strings():
    assert fr'hi\ {1}' == r'hi\ 1'
    assert fr'\n {1}' == r'\n 1'
    assert RF'\n {1}' == r'\n 1'
    assert FR'\n {1}' == r'\n 1'


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


def test_upper_case_f():
    thing = 'world'
    assert F'hello {thing}' == 'hello world'


def test_implicitly_joined():
    assert 'hello {1} ' f'hi {1}' == 'hello {1} hi 1'
    assert f'hello {1} ' 'hi {1}' == 'hello 1 hi {1}'
    s = (
        f'hi {1} '
        'hello {1}'
    )
    assert s == 'hi 1 hello {1}'
    s = f'hi {1} ' \
        'hello {1}'
    assert s == 'hi 1 hello {1}'


def _assert_fails_with_msg(s, expected_msg):
    with pytest.raises(SyntaxError) as excinfo:
        future_fstrings._fstring_parse_outer(s, 0, 0, [], [])
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


def test_no_curly_at_end():
    _assert_fails_with_msg("'{x!s{y}}'", "f-string: expecting '}'")


@xfailif_native
def test_better_error_messages():
    with pytest.raises(SyntaxError) as excinfo:
        future_fstrings.decode(b"def test():\n    f'bad {'\n")
    msg, = excinfo.value.args
    assert msg == (
        "f-string: expecting '}'\n\n"
        "    f'bad {'\n"
        '    ^'
    )


def test_streamreader_does_not_error_on_construction():
    future_fstrings.StreamReader(io.BytesIO(b"f'error{'"))


@xfailif_native
def test_streamreader_read():
    reader = future_fstrings.StreamReader(io.BytesIO(b"f'hi {x}'"))
    assert reader.read() == "'hi {}'.format((x))"


def test_main(tmpdir, capsys):
    f = tmpdir.join('f.py')
    f.write(
        '# -*- coding: future_fstrings\n'
        "print(f'hello {5 + 5}')\n"
    )
    assert not future_fstrings.main((f.strpath,))
    out, _ = capsys.readouterr()
    assert out == (
        '# -*- coding: future_fstrings\n'
        "print('hello {}'.format((5 + 5)))\n"
    )


def test_fix_coverage():
    """Because our module is loaded so early in python startup, coverage
    doesn't have a chance to instrument the module-level scope.

    Run this last so it doesn't interfere with tests in any way.
    """
    imp.reload(future_fstrings)
