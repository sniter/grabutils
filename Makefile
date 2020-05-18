VENV=venv
PY=$(VENV)/bin/python
TWINE=$(VENV)/bin/twine

build: clean
	rm -fr *.egg-info
	$(PY) setup.py sdist bdist_wheel

clean:
	rm -fr dist

deploy_test:
	$(TWINE) upload -u __token__ --repository testpypi dist/*

deploy:
	$(TWINE) upload -u __token__ --repository pypi dist/*

install_test:
	python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps grabutils
