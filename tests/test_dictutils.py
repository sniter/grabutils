import re

import pytest

from grabutils.dictutils import dictview


@pytest.fixture
def data() -> dictview:
    return dictview({
        'a': {'b': 1},
        'b': [{'c': 'c'}, 'd', 4, ('e', 5)],
        'c': ('d', 6),
        'd': {'e', 'f', 'g', 'h'},
        'e': None
    })


def test_value(data: dictview):
    # a = data.a
    assert data.a.value == {'b': 1}
    assert data.b[0].value == {'c': 'c'}
    assert data.b[100].value is None
    assert data.e.value is None
    assert data.not_existing_key.value is None
    assert data['not_existing_key'].value is None
    assert data[1000].value is None


def test_value_ctx(data: dictview):
    with data.a.value_ctx as value:
        assert value == {'b': 1}

    with data.b[0].value_ctx as value:
        assert value == {'c': 'c'}

    with data.b[100].value_ctx as value:
        assert value is None

    with data.e.value_ctx as value:
        assert value is None

    with data.not_existing_key.value_ctx as value:
        assert value is None

    with data['not_existing_key'].value_ctx as value:
        assert value is None

    with data.not_existing_key[1000].value_ctx as value:
        assert value is None

    with data[1000].value_ctx as value:
        assert value is None


def test_scan(data):
    assert data.scan('a').value == {'b': 1}
    assert data.scan('b.0').value == {'c': 'c'}
    assert data.scan('b.3.1').value == 5
    assert data.scan('b.100').value is None
    assert data.scan('not_existing_key').value is None
    assert data.scan('a.b.c.d.e.f.-1000').value is None


def test_regex(data):
    pattern = re.compile('^(a|b|e|f)$')
    assert data[pattern].value == [
        {'b': 1},
        [{'c': 'c'}, 'd', 4, ('e', 5)],
        None
    ]
