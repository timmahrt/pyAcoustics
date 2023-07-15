
These are development notes for myself

## Documentation

Documentation is generated with the following command:
`pdoc pyacoustics -d google -o docs`

A live version can be seen with
`pdoc pyacoustics -d google`

pdoc will read from pyacoustics, as installed on the computer, so you may need to run `pip install .` if you want to generate documentation from a locally edited version of pyacoustics.

## Tests

Tests are run with

`pytest --cov=pyacoustics tests/`

## Release

Releases are built and deployed with:

`python setup.py bdist_wheel sdist`

`twine upload dist/*`

Don't forget to tag the release.
