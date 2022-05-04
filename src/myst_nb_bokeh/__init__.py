"""MyST-NB-Bokeh enables gluing and pasting Bokeh plots when using the MyST-NB Sphinx extension."""

from __future__ import annotations

__author__ = """Bryan Weber"""
__email__ = "bryan.w.weber@gmail.com"
__version__ = "0.5.3"

import json
from textwrap import dedent
from typing import TYPE_CHECKING, Optional, cast

from bokeh.embed import components, json_item
from bokeh.resources import CDN
from docutils import nodes
from IPython.display import HTML, Javascript
from IPython.display import display as ipy_display
from myst_nb.nb_glue import GLUE_PREFIX as MYST_NB_GLUE_PREFIX
from myst_nb.nodes import CellOutputBundleNode
from myst_nb.render_outputs import CellOutputRenderer, get_default_render_priority
from sphinx.domains import Domain
from sphinx.util.logging import getLogger

if TYPE_CHECKING:
    from typing import Callable

    from nbformat import NotebookNode
    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

LOGGER = getLogger(__name__)

#: The mimetype that we use for JSON output from Bokeh.
#: This is a custom mimetype to avoid conflicting with any actual mimetypes.
JB_BOKEH_MIMETYPE: str = "application/jupyter-book-bokeh-json"


def setup(app: Sphinx) -> dict[str, str]:
    """Set up the MyST-NB-Bokeh Sphinx extension.

    This function is automatically called by Sphinx, as long as this extension is listed in the
    list of extensions in your Sphinx ``conf.py`` file.

    :param app: The Sphinx application, which is always passed by Sphinx during the initialization
                process.
    :return: A dictionary containing the version of this extension.
    """
    app.setup_extension("myst_nb")
    app.connect("config-inited", add_our_configuration)
    app.add_domain(BokehGlueDomain)
    app.connect("html-page-context", install_bokeh)
    return {"version": __version__}


def install_bokeh(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict,
    doctree: Optional[nodes.Node],
) -> None:  # noqa: E501
    """Add BokehJS files to the page, if the page has Bokeh plots.

    Designed to be connected to the ``'html-page-context'``
    `Sphinx event <https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-html-page-context>`__.
    If the builder format is not an HTML file, this function does nothing. The function signature
    is determined by the Sphinx API.

    :param app: The Sphinx application instance.
    :param pagename: The page being processed.
    :param templatename: The template in use.
    :param context: The context dictionary for the template.
    :param doctree: The doctree being processed.
    """  # noqa: E501
    # According to mypy, the HTML builder does not have a
    # format attribute. Probably mistyped in Sphinx
    if app.builder.format != "html":  # type: ignore
        return

    # According to mypy, the BuilderEnvironment does not have
    # a get_domain attribute. Probably mistyped in Sphinx
    domain = cast(BokehGlueDomain, app.env.get_domain("bokeh_glue"))  # type: ignore
    if domain.has_bokeh(pagename):
        from bokeh.resources import CDN

        for js_file in CDN.js_files:
            app.add_js_file(js_file)
        for js_raw in CDN.js_raw:
            # Sphinx actually allows None as the first argument to allow a string as the body
            # of the script element. For some reason, the function is not typed this way.
            app.add_js_file(None, body=js_raw, type="text/javascript")  # type: ignore


def add_our_configuration(app: Sphinx, config: Config) -> None:
    """Add the configuration for MyST-NB to the Sphinx configuration.

    Designed to be connected to the ``'config-inited'``
    `Sphinx event <https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-config-inited>`__
    to ensure that all configuration sources have been read. The function signature is determined
    by the Sphinx API.

    :param app: The Sphinx application instance.
    :param config: The Sphinx configuration instance.
    """
    if app.config.nb_render_priority and "html" in app.config.nb_render_priority:
        html_render_priority = list(app.config.nb_render_priority.get("html"))
    else:
        html_render_priority = list(get_default_render_priority("html"))

    if JB_BOKEH_MIMETYPE not in html_render_priority:
        if app.config.nb_render_priority and "html" in app.config.nb_render_priority:
            LOGGER.warning(
                "'nb_render_priority' has been configured and does not contain the MyST-NB "
                "Bokeh-specific mimetype. We will attempt to insert the MyST-NB Bokeh "
                "mimetype at the top of the 'html' rendering priority."
            )
        app.config["nb_render_priority"] = {
            "html": [JB_BOKEH_MIMETYPE] + html_render_priority
        }

    if app.config.nb_render_plugin not in ("default", "bokeh"):
        LOGGER.warning(
            "'nb_render_plugin' has been configured, perhaps in your conf.py. Not "
            "changing the value at this time."
        )
    else:
        app.config["nb_render_plugin"] = "bokeh"


class BokehGlueDomain(Domain):
    """A Sphinx domain for handling Bokeh data."""

    #: The name of this domain
    name = "bokeh_glue"
    #: The label used for this domain
    label = "BokehGlue"
    #: Data version, bump this when the format of ``self.data`` changes
    data_version = 1
    #: Data value for a fresh environment.
    #: ``has_bokeh`` is a mapping of docnames to a Boolean whether or not it has Bokeh
    initial_data: dict[str, dict[str, bool]] = {
        "has_bokeh": {},
    }

    def has_bokeh(self, docname: Optional[str] = None) -> bool:
        """Return whether or not this page requires BokehJS.

        :param docname: The name of the document being processed.
        :return: Boolean whether or not the page requires BokehJS.
        """
        if docname:
            return self.data["has_bokeh"].get(docname, False)
        else:
            return any(self.data["has_bokeh"].values())

    def process_doc(
        self, env: BuildEnvironment, docname: str, document: nodes.document
    ) -> None:
        """Set internal data for whether or not this page requires BokehJS.

        :param env: The Sphinx build environment instance.
        :param docname: The name of the page being processed.
        :param document: The doctree of the current page.
        """

        def bokeh_in_output(node: nodes.Node) -> bool:
            """Whether or not Bokeh JSON is in the output."""
            if not isinstance(node, CellOutputBundleNode):
                return False
            return any(
                output.get("metadata", {}).get("scrapbook", {}).get("has_bokeh", False)
                for output in node.outputs
            )

        self.data["has_bokeh"][docname] = any(document.traverse(bokeh_in_output))


def glue_bokeh(name: str, variable: object, display: bool = False) -> None:
    """Glue Bokeh figures into the cell output.

    :param name: The name to give to the ``variable`` in the cell output. This name must be used
                 when pasting this output in other cells.
    :param variable: The object to be inserted into the cell output. Note that the object itself
                     is not stored. Rather, this function inserts the JSON representation of the
                     plot into the cell output, which must then be extracted and shown by the
                     `~myst_nb_bokeh.BokehOutputRenderer`.
    :param display: If ``True``, the plot will be shown in the output of the cell. Useful for
                    sanity checking the output. ``False`` by default.
    """
    mime_prefix = "" if display else MYST_NB_GLUE_PREFIX
    metadata = {"scrapbook": dict(name=name, mime_prefix=mime_prefix, has_bokeh=True)}
    ipy_display(
        {
            mime_prefix
            + JB_BOKEH_MIMETYPE: json.dumps(
                json_item(variable, name), separators=(",", ":")
            )
        },
        raw=True,
        metadata=metadata,
    )
    if display:
        script, div = components(variable, wrap_script=False)
        s = Javascript(script, lib=CDN.js_files[0])
        h = HTML(div)
        ipy_display(h, s)


class BokehOutputRenderer(CellOutputRenderer):
    """Render Bokeh JSON output from a cell's output.

    This class extends the `~myst_nb.render_outputs.CellOutputRenderer` class to add a method that
    renders Bokeh JSON output into a ``<div>`` element in the page. We do this by adding a new key
    to the ``_render_map`` attribute of `~myst_nb.render_outputs.CellOutputRenderer`. The key is
    the value of the `~myst_nb_bokeh.JB_BOKEH_MIMETYPE` module data member.
    """

    _render_map: dict[str, Callable[[NotebookNode, int], list[nodes.Node]]]

    def __init__(self, *args, **kwargs):
        """Initialize the `BokehOutputRenderer`.

        Any positional or keyword arguments are passed to the superclass constructor. This class
        takes no additional arguments.
        """
        super().__init__(*args, **kwargs)
        self._render_map[JB_BOKEH_MIMETYPE] = self.render_bokeh

    def render_bokeh(self, output: NotebookNode, index: int) -> list[nodes.Node]:
        """Output Sphinx nodes for Bokeh plots given the JSON of the plot.

        :param output: The output nodes from the cell. `~nbformat.NotebookNode` instances can be
                       accessed like dictionaries.
        :param index: The cell index.
        :return: A `list` of ``docutils.nodes.Node`` instances. The two nodes returned here are the
                 ``<div>`` that will contain the plot and a ``<script>`` with the appropriate
                 BokehJS call to turn the JSON into a plot.
        """
        name = output["metadata"]["scrapbook"]["name"]
        html_node = nodes.raw(text=f'<div id="{name}"></div>', format="html")

        json_text = output["data"][JB_BOKEH_MIMETYPE]
        js_text = dedent(
            f"""\
            <script type="text/javascript">
              Bokeh.embed.embed_item(
                  {json_text}
              );
            </script>"""
        )
        js_node = nodes.raw(text=js_text, format="html")

        return [html_node, js_node]
