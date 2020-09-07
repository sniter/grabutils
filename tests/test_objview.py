import typing as t

import pytest

from grabutils.objview import Project, ObjectView, Zip


@pytest.fixture
def data1() -> dict:
    return {
        'current': {
            'field': ['is', 'too', {'nested': True}],
            'fields': ['a', 'b', 'c'],
            'values': [1, 2, 3],
            'notfoo': 'notfoo',
            'nested': [
                {'currency': 'USD', 'amount': 600.},
                {'currency': 'AUD', 'amount': 1200.},
                {'currency': 'EUR', 'amount': 30.},
            ]
        },
        'data': {
            'aaaaaa': {
                'content': 'Hello, World'
            },
            'dddddd': {
                'content': 'Shalom!'
            },
            'bbbbb': {
                '__ref': 'aaaaaa'
            },
            'cccccc': {
                '__refs': ['bbbbb', 'dddddd']
            }
        }
    }


@pytest.fixture
def model_class1() -> t.Type[ObjectView]:
    class Ref(Project):
        """
        Ref substitutor
        """

        def __init__(self, ref_path: t.Iterable[any], *path, **kwargs):
            super(Ref, self).__init__(*path, **kwargs)
            self.ref_path = ref_path

    class MyView(ObjectView):
        is_nested = Project('current', 'field', 2, 'nested')
        is_too = Project('current', 'field', 1)
        is_keyerror = Project('current', 'fake')
        is_keyerror2 = Project('current', 0)

        transpose = Zip(
            Project('current', 'fields'),
            Project('current', 'values'),
        )
        transpose1 = Zip(
            Project('current', 'fields'),
            Project('current', 'values'),
            astype=dict
        )
        constant = 4

        def attr_foo(self, obj):
            return obj['current']['notfoo']

    return MyView


def test_objview1(data1: dict, model_class1: t.Type[ObjectView]):
    model = model_class1(data1)

    assert isinstance(model.is_nested, bool)
    assert model.is_nested is True
    assert model.is_too == 'too'

    with pytest.raises(KeyError):
        assert model.is_keyerror is None

    with pytest.raises(KeyError):
        assert model.is_keyerror2 == 10

    assert model.transpose == [
        ('a', 1),
        ('b', 2),
        ('c', 3),
    ]

    assert model.transpose1 == {
        'a': 1,
        'b': 2,
        'c': 3,
    }

    assert model.constant == 4

    assert model.foo == 'notfoo'
