import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="grabutils",
    version="0.0.9",
    author="Ilya Babich",
    author_email="sniter@gmail.com",
    description="Utils and helpers for crawling websites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sniter/grabutils",
    install_requires=[
        'beautifulsoup4',
        'lxml'
    ],
    tests_require=[
        'pytest'
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
