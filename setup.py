import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

bs_deps = [
    'beautifulsoup4',
    'lxml'
]

ssh_deps = [
    'paramiko[ed25519]',
    'scp',
]
rest_deps = [
    'requests'
]

setuptools.setup(
    name="grabutils",
    version="0.0.21",
    author="Ilya Babich",
    author_email="sniter@gmail.com",
    description="Utils and helpers for crawling websites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sniter/grabutils",
    install_requires=[],
    extras_require={
        'bs': bs_deps,
        'ssh': ssh_deps,
        'rest': rest_deps,
        'all': bs_deps + ssh_deps + rest_deps
    },
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
