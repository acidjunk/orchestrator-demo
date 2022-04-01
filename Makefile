SHELL = /bin/sh

docs:
	$(MAKE) -C docs O="-j auto -a " html

livehtml:
	sphinx-autobuild -B docs docs/_build/html

clean:
	# Clean up all build results
	rm -rf docs/_build
	# Clean up coverage results
	rm -rf ./htmlcov
	rm -f coverage.xml
	# Clean up .pyc files
	find . -name "*.pyc" -exec rm {} \;

.PHONY: docs livehtml clean
