# The targets in this makefile should be executed inside Poetry, i.e. `poetry run make
# docs`.

.PHONY: docs

default: mypy-generate test-generate generate test-import mypy-cdp test-cdp

docs:
	$(MAKE) -C docs html

generate:
	python generator/generate.py

mypy-cdp:
	mypy trio_cdp/

mypy-generate:
	mypy generator/

test-cdp:
	pytest tests/ --cov=trio_cdp --cov-report=term-missing

test-generate:
	pytest generator/

test-import:
	python -c 'import trio_cdp; print(trio_cdp.accessibility)'
