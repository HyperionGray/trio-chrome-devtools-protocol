all:

publish:
	rm -fr dist trio_chrome_devtools_protocol.egg-info
	$(PYTHON) setup.py sdist
	twine upload dist/*
