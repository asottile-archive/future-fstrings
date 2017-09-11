# -*- coding: future_fstrings -*-
def test_hello_world():
    thing = 'world'
    assert f'hello {thing}' == 'hello world'


def test_maths():
    assert f'{5 + 5}' == '10'
