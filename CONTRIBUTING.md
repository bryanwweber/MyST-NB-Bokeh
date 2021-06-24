# Contribute to MyST-NB-Bokeh

[![Github-CI][github-ci]][github-link]
[![Code style: black][black-badge]][black-link]

We welcome all contributions! Although this project is not affiliated with the [Executable Books Project](https://executablebooks.org), you can see the [EBP Contributing Guide](https://executablebooks.org/en/latest/contributing.html) for general details, and below for guidance specific to MyST-NB-Bokeh.

## Installation

To install `MyST-NB-Bokeh` for package development:

```bash
git clone https://github.com/bryanwweber/MyST-NB-Bokeh
cd MyST-NB-Bokeh
python -m pip install -e .[code_style,testing,docs]
```

## Code Style

Code style is tested using [flake8](http://flake8.pycqa.org), with the configuration set in `setup.cfg`, and code formatted with [black](https://github.com/ambv/black).

Installing with `myst-nb-bokeh[code_style]` makes the [pre-commit](https://pre-commit.com/) package available, which will ensure this style is met before commits are submitted, by reformatting the code and testing for lint errors. It can be setup by:

```shell
>> cd MyST-NB-Bokeh
>> pre-commit install
```

Optionally you can run `black` and `flake8` separately:

```shell
>> black .
>> flake8 .
```

Editors like VS Code also have automatic code reformat utilities, which can adhere to this standard.

All functions and class methods should be annotated with types and include a docstring. The prefered docstring format is outlined in `MyST-NB/docstring.fmt.mustache` and can be used automatically with the [autodocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) VS Code extension.

## Testing

For code tests, MyST-NB-Bokeh uses [pytest](https://docs.pytest.org):

```shell
>> cd MyST-NB-bokeh
>> pytest
```

## Unit Testing

Testing is one of the most important aspects of your PR. You should write test cases and verify your implementation by following the testing guide above. If you modify code related to existing unit tests, you must run appropriate commands and confirm that the tests still pass.

Note that we are using [pytest](https://docs.pytest.org/en/latest/) for testing, [pytest-regression](https://pytest-regressions.readthedocs.io/en/latest/) to self-generate/re-generate expected outcomes of test and [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) for checking coverage.

To run tests along with coverage:

```shell
pytest -v --cov=myst_nb
```

To run tests along with generation of an HTML coverage report:

```shell
pytest -v --cov=myst_nb_bokeh --cov-report=html
```

### Test File and Directory Naming Conventions

Tests are found in the [tests](https://github.com/executablebooks/MyST-NB/tree/master/tests) directory. In order for `pytest` to find the test scripts correctly, the name of each test script should start with `test_` prefix.

### How to Write Tests

There are many examples of unit tests under the [tests](https://github.com/executablebooks/MyST-NB/tree/master/tests) directory, so reading some of them is a good and recommended way. Prefer using the `fixtures` and the classes defined in [conftest.py](https://github.com/executablebooks/MyST-NB/blob/master/tests/conftest.py) as much as possible.

If using [pytest-regression](https://pytest-regressions.readthedocs.io/en/latest/), a new directory with `test_` prefix is expected to be created in the first test run. This will store your expected output against which subsequent test outputs will be compared.

### Code Coverage report

[pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) is used to generate code coverage report. Make sure that your test cases cover most of the code written by you.

[github-ci]: https://github.com/bryanwweber/MyST-NB-Bokeh/workflows/continuous-integration/badge.svg?branch=main
[github-link]: https://github.com/bryanwweber/MyST-NB-Bokeh
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]: https://github.com/ambv/black
