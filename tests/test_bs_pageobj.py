import operator as op

import pytest

from grabutils.bs.pageobj import (
    BsField, BsPageObj, PageObject, Href, Image, Nested,
    inner_text, stripped, as_attr, List
)


class PageObjectConstant(PageObject):
    hrefs = BsField('a', as_attr('href'), many=True)
    labels = BsField('a', inner_text, many=True)
    divs = BsField('div', inner_text, many=True)
    constant1 = 1

    @staticmethod
    def attr_fname(*args, **kwargs):
        return 'fname'

    @property
    def constant2(self):
        return 2

    class Meta:
        # fields = 'href', 'label', 'constant1', 'constant2'
        ignore_fields = 'divs',


class Language1(BsPageObj):
    href = BsField('a', as_attr('href'), many=True)
    label = BsField('a', inner_text, many=True)


class Language2(BsPageObj):
    href = BsField(None, as_attr('href'))
    label = BsField(None, inner_text)


class Language3(BsPageObj):
    languages = BsField('a', Nested(Language2), many=True)


class PageObject(BsPageObj):
    paragraph = BsField('p', inner_text, stripped)
    link = Href('.test-url')
    image = Image('.test-img')

    items = BsField('ul > li', inner_text, stripped, many=True)
    languages = BsField('.languages a', inner_text, many=True)
    languages_1 = BsField('.languages', Nested(Language1))
    languages_2 = BsField('.languages a', Nested(Language2), many=True)
    languages_3 = BsField('.languages > div', List(BsField('a', Nested(Language2), many=True)), many=True)

    _invisible = BsField('.languages a', inner_text, many=True)

    @property
    def custom_field(self):
        return [
            v for idx, v in enumerate(self._invisible)
            if idx in (1, 2, 4)
        ]


@pytest.fixture(scope="module")
def page(html):
    return PageObject(html)


def test_page_object(html):
    pageobj = PageObjectConstant(html)
    value = pageobj.as_dict()

    assert value == {
        'constant1': 1,
        'constant2': 2,
        'fname': 'fname',
        'hrefs': ['https://www.python.org/',
                  'http://ada',
                  'https://java',
                  'http://cpp',
                  'http://cobol',
                  'http://d',
                  'http://go'],
        'labels': ['Python', 'Ada', 'Java', 'C++', 'Cobol', 'D', 'Go']
    }


def test_link(page):
    link = page.link

    assert 'href' in link
    assert link['href'] == 'https://www.python.org/'

    assert 'label' in link
    assert link['label'] == 'Python'


def test_paragraph(page):
    assert (page.paragraph == "Hello, world!")


def test_image(page):
    image = page.image

    assert 'src' in image
    assert image['src'] == 'https://www.python.org/static/img/python-logo@2x.png'

    assert 'label' in image
    assert image['label'] == 'Python logo'


def test_items(page: PageObject):
    items = page.items

    assert items == ['Alpha', 'Beta', 'Gamma']


def test_nested(page: PageObject):
    languages = page.languages
    languages_1 = page.languages_1
    languages_2 = page.languages_2
    languages_3 = page.languages_3

    assert languages == ['Ada', 'Java', 'C++', 'Cobol', 'D', 'Go']
    assert languages_1 == {
        'href': ['http://ada', 'https://java', 'http://cpp', 'http://cobol', 'http://d', 'http://go'],
        'label': ['Ada', 'Java', 'C++', 'Cobol', 'D', 'Go']
    }
    assert languages_2 == [
        {'href': 'http://ada', 'label': 'Ada'},
        {'href': 'https://java', 'label': 'Java'},
        {'href': 'http://cpp', 'label': 'C++'},
        {'href': 'http://cobol', 'label': 'Cobol'},
        {'href': 'http://d', 'label': 'D'},
        {'href': 'http://go', 'label': 'Go'}
    ]
    assert languages_3 == [
        [{'href': 'http://ada', 'label': 'Ada'}, {'href': 'https://java', 'label': 'Java'}],
        [{'href': 'http://cpp', 'label': 'C++'}],
        [{'href': 'http://cobol', 'label': 'Cobol'}],
        [{'href': 'http://d', 'label': 'D'}, {'href': 'http://go', 'label': 'Go'}]
    ]
    assert page.custom_field == [
        'Java', 'C++', 'D'
    ]

    assert '_invisible' not in page.as_dict()
    assert 'custom_field' in page.as_dict()
