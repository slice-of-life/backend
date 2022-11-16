# Makefile for slice of life backend 

help:
	@echo "help -- show this message and exit (default)"
	@echo "venv -- create the virtual environment"
	@echo "clean-venv -- destroy the virtual environment"
	@echo "test -- run tests"
	@echo "lint -- run linter"
	@echo "bootstrap -- bootstrap project in virtual environment"
	@echo "activate -- instructions for activating the virtual environment"
	@echo "clean -- remove all generated artifacts; doesn't destroy virtual environment"

venv:
	[ -d .venv ] || python3 -m venv .venv --prompt=backend

clean-venv:
	[ ! -d .venv ] || rm -rf .venv

clean-test:
	[ ! -d .pytest_cache ] || rm -rf .pytest_cache

clean-pyc:
	find . -name __pycache__ -exec rm -rf {} +
	find . -name *.egg-info -exec rm -rf {} +

clean-cov:
	[ ! -e .coverage ] || rm -f .coverage

clean: clean-venv clean-test clean-pyc clean-cov

activate:
	@echo 
	@echo
	@echo "Virtual environment created!"
	@echo "Activate it by running the following:"
	@echo
	@echo "    source .venv/bin/activate"
	@echo 
.PHONY: test
test:
	pytest --cov=api --verbose test/

.PHONY: lint
lint:
	pylint src/sliceoflife_webservice

bootstrap: venv
	@( \
		source .venv/bin/activate; \
		pip3 install --require-virtualenv -r requirements.txt; \
		pip3 install --editable . ; \
	)
	@$(MAKE) activate

serve:
	gunicorn sliceoflife_webservice:app --log-level 'debug'
