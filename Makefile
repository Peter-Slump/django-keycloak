install-python:
	pip install --upgrade setuptools
	pip install -e .
	pip install "file://`pwd`#egg=django-keycloak[dev,doc]"

bump-patch:
	bumpversion patch

bump-minor:
	bumpversion minor

deploy-pypi: clear
	python3 -c "import sys; sys.version_info >= (3, 5, 3) or sys.stdout.write('Python version must be greatest then 3.5.2\n') or exit(1)"
	python3 setup.py sdist bdist_wheel
	twine upload dist/*