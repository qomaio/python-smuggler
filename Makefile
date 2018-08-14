all:
	python setup.py clean
	python setup.py install
	python scripts/smuggler_test.py
