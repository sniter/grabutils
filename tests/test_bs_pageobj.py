import operator as op

import pytest

from grabutils.bs.pageobj import BsField, BsPageObj, Href, Image


class PageObject(BsPageObj):
    paragraph = BsField('p', op.attrgetter('string'), op.methodcaller('strip'))
    link = Href('.test-url')
    image = Image('.test-img')

    items = BsField('ul > li', op.attrgetter('string'), op.methodcaller('strip'), many=True)


@pytest.fixture(scope="module")
def page(html):
    return PageObject(html)


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


def test_items(page):
    items = page.items

    assert items == ['Alpha', 'Beta', 'Gamma']
