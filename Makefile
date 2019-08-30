.PHONY: test
	
all:

publish:
	rm -fr dist trio_chrome_devtools_protocol.egg-info
	$(PYTHON) setup.py sdist
	twine upload dist/*

test:
	$(PYTHON) -m pytest test/ --cov=trio_cdp --cov-report=term-missing
