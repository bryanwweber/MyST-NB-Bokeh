# Welcome to MyST-NB-Bokeh's documentation

This extension provides an interface to glue and paste [Bokeh](https://bokeh.org/) figures in the output of Jupyter Notebook cells when using the [MyST-NB](https://myst-nb.readthedocs.io/en/latest/index.html) library for Sphinx.

MyST-NB can already _display_ Bokeh figures in its built output, using functionality built-in to Bokeh. For more information about this, see the [MyST-NB documentation](https://myst-nb.readthedocs.io/en/latest/render/interactive.html#bokeh). However, [_gluing_](https://myst-nb.readthedocs.io/en/latest/render/glue.html#save-variables-in-code-cells) and [_pasting_](https://myst-nb.readthedocs.io/en/latest/render/glue.html#embedding-variables-in-the-page) Bokeh figures (for example, into a MyST `Figure` directive) is not possible with the base MyST-NB package.

That's where this extension comes in 😀

## Installing

MyST-NB-Bokeh can be installed with `pip` or `conda`. Python versions higher than 3.10 are supported.

```shell
python -m pip install myst-nb-bokeh
```

or

```shell
conda install -c conda-forge myst-nb-bokeh
```

MyST-NB-Bokeh supports version 1.0.0 of MyST-NB. Older versions have not been tested, but we guess that anything 0.14.0 and higher should work.

:::{toctree}
---

maxdepth: 2
caption: "Contents:"
---

bokeh
api
:::

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
