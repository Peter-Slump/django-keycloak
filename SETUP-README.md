* Docs source: https://packaging.python.org/en/latest/tutorials/packaging-projects/


python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
python3 -m build                            # Generate distribution archives
python3 -m pip install --upgrade twine
python3 -m twine upload dist/*              # Upload the distribution archives

