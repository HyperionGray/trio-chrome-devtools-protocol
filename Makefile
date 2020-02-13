.PHONY: test

publish: test
	rm -fr dist trio_chrome_devtools_protocol.egg-info
	python setup.py sdist
	twine upload dist/*

test:
	pytest test/ --cov=trio_cdp --cov-report=term-missing
