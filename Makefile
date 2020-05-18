VENV=venv
PY=$(VENV)/bin/python
TWINE=$(VENV)/bin/twine

build: clean
	$(PY) setup.py sdist bdist_wheel

clean:
	rm -fr dist

deploy_test:
	$(TWINE) upload -u __token__ --repository testpypi dist/*
