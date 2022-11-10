# Makefile for monopoly-pygame

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

clean:
	rm -rf .pytest_cache

activate: venv
	@echo "Virtual environment created!"
	@echo "Activate it by running the following:"
	@echo "    source .venv/bin/activate"

.PHONY: test
test:
	pytest --verbose --rootdir=test

.PHONY: lint
lint:
	python3 -m pylint src

bootstrap: activate
	[ ! .venv ] || pip3 install --require-virtualenv -r requirements.txt 
	[ ! .venv ] || pip3 install --editable .

