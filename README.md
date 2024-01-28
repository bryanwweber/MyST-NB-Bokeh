# MyST-NB-Bokeh

[![PyPI status](https://img.shields.io/pypi/v/myst-nb-bokeh.svg)](https://pypi.org/project/myst-nb-bokeh)
[![continuous-integration](https://github.com/bryanwweber/MyST-NB-Bokeh/actions/workflows/test.yml/badge.svg)](https://github.com/bryanwweber/MyST-NB-Bokeh/actions/workflows/test.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/bryanwweber/MyST-NB-Bokeh/main.svg)](https://results.pre-commit.ci/latest/github/bryanwweber/MyST-NB-Bokeh/main)
[![Documentation Status](https://readthedocs.org/projects/myst-nb-bokeh/badge/?version=latest)](https://myst-nb-bokeh.readthedocs.io/en/latest/?badge=latest)

MyST-NB-Bokeh includes functions for gluing and pasting Bokeh figures in MyST-NB documents.

## Install

```shell
python -m pip install myst-nb-bokeh
```

## Setup and Development

The repo is set up to use [mise](https://mise.jdx.dev) to install required tools. Once `mise` is installed, changing into this directory should install the correct tools with the right versions. Then run `pdm install` to install development dependencies. Running `pdm test` will run the tests. `pdm docs` will build the docs site.
