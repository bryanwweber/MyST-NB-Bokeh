"""MyST-NB-Bokeh enables gluing and pasting Bokeh plots when using the MyST-NB Sphinx extension."""

from __future__ import annotations

__author__ = """Bryan Weber"""
__email__ = "bryan.w.weber@gmail.com"
__version__ = "0.1.0"

import json
import logging
from textwrap import dedent
from typing import TYPE_CHECKING, Optional, cast

from bokeh.embed import components, json_item
from bokeh.resources import CDN
from docutils import nodes
from IPython.display import HTML, Javascript
from IPython.display import display as ipy_display
from myst_nb.nb_glue import GLUE_PREFIX as MYST_NB_GLUE_PREFIX
from myst_nb.nodes import CellOutputBundleNode
from myst_nb.render_outputs import CellOutputRenderer
from sphinx.domains import Domain

if TYPE_CHECKING:
    from typing import Any, Callable

    from docutils.nodes import Node
    from nbformat import NotebookNode
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment

LOGGER = logging.getLogger(__name__)

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
    app.add_domain(BokehGlueDomain)

    nb_render_priority = {
        "html": (
            "application/jupyter-book-bokeh-json",
            "application/vnd.jupyter.widget-view+json",
            "application/javascript",
            "text/html",
            "image/svg+xml",
            "image/png",
            "image/jpeg",
            "text/markdown",
            "text/latex",
            "text/plain",
        )
    }
    # Sphinx config is a dictionary with keys accessible as attributes
    # Mypy just doesn't understand :-(
    app.config.nb_render_priority = nb_render_priority  # type: ignore

    # Load bokeh
    def install_bokeh(
        app: Sphinx,
        pagename: str,
        templatename: str,
        context: dict,
        event_arg: Any,
    ) -> None:
        if app.builder.format != "html":
            return

        domain = cast(BokehGlueDomain, app.env.get_domain("bokeh_glue"))
        if domain.has_bokeh(pagename):
            from bokeh.resources import CDN

            for js_file in CDN.js_files:
                app.add_js_file(js_file)
            for js_raw in CDN.js_raw:
                # Sphinx actually allows None as the first argument to allow a string as the body
                # of the script element.
                app.add_js_file(None, body=js_raw, type="text/javascript")  # type: ignore

    app.connect("html-page-context", install_bokeh)
    return {"version": __version__}


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
        """Return whether or not this page requires BokehJS."""
        if docname:
            return self.data["has_bokeh"].get(docname, False)
        else:
            return any(self.data["has_bokeh"].values())

    def process_doc(
        self, env: "BuildEnvironment", docname: str, document: nodes.document
    ) -> None:
        """Set internal data for whether or not this page requires BokehJS."""

        def bokeh_in_output(node: "Node") -> bool:
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
