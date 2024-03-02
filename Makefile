.PHONY: clean clean-test clean-pyc clean-build test
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +	

clean-pyc: ## remove Python file artifacts
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	@find . -name '*.pdf' -exec rm -f {} +
	@rm -f .coverage
	@rm -fr htmlcov/

lint: ## check style with black
	@black pdfdoc/*.py
	@black pdfdoc/contentrect/*.py
	@black pdfdoc/document/*.py
	@black pdfdoc/graphics/*.py
	@black pdfdoc/labeldoc/*.py
	@black pdfdoc/scripts/*.py
	@black pdfdoc/style/*.py
	@black pdfdoc/tablecell/*.py
	@black tests/*.py


lint-check: ## check if lint status is consistent between commits
	@black --diff --check pdfdoc/*.py
	@black --diff --check pdfdoc/contentrect/*.py
	@black --diff --check pdfdoc/document/*.py
	@black --diff --check pdfdoc/graphics/*.py
	@black --diff --check pdfdoc/labeldoc/*.py
	@black --diff --check pdfdoc/scripts/*.py
	@black --diff --check pdfdoc/style/*.py
	@black --diff --check pdfdoc/tablecell/*.py
	@black --diff --check tests/*.py

test: ## run tests quickly with the default Python
	@py.test -s -v --cov
	
coverage: ## check code coverage quickly with the default Python
	coverage run --source pdfdoc -m pytest
	coverage report -m
	coverage html
	open htmlcov/index.html

release: clean dist ## package and upload a release
	twine check dist/*
	twine upload dist/*

dist: clean ## builds source and wheel package
	@python -m build
	@twine check dist/*
	@ls -l dist

install: clean ## install the package to the active Python's site-packages
	@pip install .
