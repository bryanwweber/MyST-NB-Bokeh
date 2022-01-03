# Welcome to MyST-NB-Bokeh's documentation!

This extension provides an interface to glue and paste [Bokeh](https://bokeh.org/) figures in the output of Jupyter Notebook cells when using the [MyST-NB](https://myst-nb.readthedocs.io/en/latest/index.html) library for Sphinx.

MyST-NB can already _display_ Bokeh figures in its built output, using functionality built-in to Bokeh. For more information about this, see the [MyST-NB documentation](https://myst-nb.readthedocs.io/en/latest/examples/interactive.html#bokeh). However, [_gluing_](https://myst-nb.readthedocs.io/en/latest/use/glue.html#gluing-variables-in-your-notebook) and [_pasting_](https://myst-nb.readthedocs.io/en/latest/use/glue.html#pasting-glued-variables-into-your-page) Bokeh figures (for example, into a MyST `Figure` directive) is not possible with the base MyST-NB package.

That's where this extension comes in 😀

## Installing

MyST-NB-Bokeh can currently be installed only with `pip`. It relies on an unreleased version of MyST-NB, due to a bug that is fixed in [MyST-NB pull request #337](https://github.com/executablebooks/MyST-NB/pull/337), so you have to install MyST-NB _first_ before MyST-NB-Bokeh:

```shell
python -m pip install https://github.com/executablebooks/MyST-NB/archive/refs/heads/master.zip
python -m pip install myst-nb-bokeh
```

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
