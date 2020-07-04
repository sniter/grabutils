VENV=venv
PY=$(VENV)/bin/python
TWINE=$(VENV)/bin/twine

build: clean
	$(PY) setup.py sdist bdist_wheel

clean:
	rm -fr dist
	rm -fr *.egg-info

deploy_test: build
	$(TWINE) upload -u __token__ --repository testpypi dist/*

deploy: build
	$(TWINE) upload -u __token__ --repository pypi dist/*

install_test:
	python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps grabutils
