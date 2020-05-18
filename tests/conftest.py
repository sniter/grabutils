import pytest


@pytest.fixture(scope="module")
def html():
    with open('tests/index.html') as html:
        html_content = html.read()
    return html_content
