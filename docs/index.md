# Welcome to MyST-NB-Bokeh's documentation!

This extension provides an interface to glue and paste [Bokeh](https://bokeh.org/) figures in the output of Jupyter Notebook cells when using the [MyST-NB](https://myst-nb.readthedocs.io/en/latest/index.html) library for Sphinx.

MyST-NB can already _display_ Bokeh figures in its built output, using functionality built-in to Bokeh. For more information about this, see the [MyST-NB documentation](https://myst-nb.readthedocs.io/en/latest/examples/interactive.html#bokeh). However, [_gluing_](https://myst-nb.readthedocs.io/en/latest/use/glue.html#gluing-variables-in-your-notebook) and [_pasting_](https://myst-nb.readthedocs.io/en/latest/use/glue.html#pasting-glued-variables-into-your-page) Bokeh figures (for example, into a MyST `Figure` directive) is not possible with the base MyST-NB package.

That's where this extension comes in 😀

## Installing

MyST-NB-Bokeh can be installed with `pip` or `conda`. Python versions higher than 3.7 are supported.

```shell
python -m pip install myst-nb-bokeh
```

or

```shell
conda install -c conda-forge myst-nb-bokeh
```

MyST-NB-Bokeh supports version 0.13.2 of MyST-NB.

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
