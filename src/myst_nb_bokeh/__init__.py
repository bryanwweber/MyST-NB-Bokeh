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
JB_BOKEH_MIMETYPE = "application/jupyter-book-bokeh-json"
GLUE_PREFIX = "application/papermill.record/"


def setup(app: "Sphinx") -> dict[str, str]:
    app.setup_extension("myst_nb")
    app.add_domain(BokehGlueDomain)

    # Load bokeh
    def install_bokeh(
        app: "Sphinx",
        pagename: str,
        templatename: str,
        context: dict,
        event_arg: "Any",
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

    name = "bokeh_glue"
    label = "BokehGlue"
    # data version, bump this when the format of self.data changes
    data_version = 1
    # data value for a fresh environment
    # - has_bokeh is the mapping of docnames to a boolean whether or not it has Bokeh
    initial_data: dict[str, dict[str, bool]] = {
        "has_bokeh": {},
    }

    def has_bokeh(self, docname: Optional[str] = None) -> bool:
        if docname:
            return self.data["has_bokeh"].get(docname, False)
        else:
            return any(self.data["has_bokeh"].values())

    def process_doc(
        self, env: "BuildEnvironment", docname: str, document: nodes.document
    ) -> None:
        def bokeh_in_output(node: "Node") -> bool:
            """Whether or not Bokeh JSON is in the output."""
            if not isinstance(node, CellOutputBundleNode):
                return False
            return any(
                output.get("metadata", {}).get("scrapbook", {}).get("has_bokeh", False)
                for output in node.outputs
            )

        self.data["has_bokeh"][docname] = any(document.traverse(bokeh_in_output))


def glue_bokeh(name, variable, display=False):
    mime_prefix = "" if display else GLUE_PREFIX
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
    _render_map: dict[str, "Callable[[NotebookNode, int], list[nodes.Node]]"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._render_map[JB_BOKEH_MIMETYPE] = self.render_bokeh

    def render_bokeh(self, output: "NotebookNode", index: int) -> list[nodes.Node]:
        """Output nodes for Bokeh plots given JSON."""
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
