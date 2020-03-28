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

publish: test-import mypy-cdp test-cdp
	rm -fr dist trio_chrome_devtools_protocol.egg-info
	python setup.py sdist
	twine upload dist/*

test-cdp:
	pytest tests/ --cov=trio_cdp --cov-report=term-missing

test-generate:
	pytest generator/

test-import:
	python -c 'import trio_cdp; print(trio_cdp.accessibility)'
