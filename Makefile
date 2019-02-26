install-python:
	pip install --upgrade setuptools
	pip install -e .
	pip install "file://`pwd`#egg=django-keycloak[dev,doc]"

bump-patch:
	bumpversion patch

bump-minor:
	bumpversion minor

deploy-pypi: clear
	python setup.py sdist bdist_wheel
	twine upload dist/*

clear:
	rm -rf dist/*
