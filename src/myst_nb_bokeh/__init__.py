"""MyST-NB-Bokeh enables gluing and pasting Bokeh plots when using the MyST-NB Sphinx extension."""
from __future__ import annotations

import json
from textwrap import dedent
from typing import TYPE_CHECKING

from bokeh.core.types import ID
from bokeh.embed import components, json_item
from bokeh.model import Model
from bokeh.resources import CDN
from docutils import nodes
from IPython.display import HTML, Javascript
from IPython.display import display as ipy_display
from myst_nb.core.render import MimeData, MimeRenderPlugin, NbElementRenderer
from myst_nb.ext.glue import GLUE_PREFIX as MYST_NB_GLUE_PREFIX
from sphinx.util.logging import getLogger

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config


__author__ = """Bryan Weber"""
__email__ = "bryan.w.weber@gmail.com"
__version__ = "1.0.0.post2"

LOGGER = getLogger(__name__)

#: The mimetype that we use for JSON output from Bokeh.
#: This is a custom mimetype to avoid conflicting with any actual mimetypes.
JB_BOKEH_MIMETYPE: str = "application/jupyter-book-bokeh-json"


def setup(app: "Sphinx") -> dict[str, str | bool]:
    """Set up the MyST-NB-Bokeh Sphinx extension.

    This function is automatically called by Sphinx, as long as this extension is
    listed in the list of extensions in your Sphinx ``conf.py`` file.

    :param app: The Sphinx application, which is always passed by Sphinx during the
                initialization process.
    :return: A dictionary containing the version of this extension.
    """
    app.setup_extension("myst_nb")
    app.connect("config-inited", add_our_configuration)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def add_our_configuration(app: Sphinx, config: Config) -> None:
    """Add the configuration for MyST-NB-Bokeh to the Sphinx configuration.

    Designed to be connected to the ``'config-inited'``
    `Sphinx event <https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-config-inited>`__
    to ensure that all configuration sources have been read. The function signature is
    determined by the Sphinx API.

    :param app: The Sphinx application instance.
    :param config: The Sphinx configuration instance.
    """  # noqa: E501
    overrides = list(app.config.nb_mime_priority_overrides[:])
    overrides.insert(0, ("html", JB_BOKEH_MIMETYPE, 0))
    app.config["nb_mime_priority_overrides"] = overrides


def glue_bokeh(name: ID, variable: Model, display: bool = False) -> None:
    """Glue Bokeh figures into the cell output.

    :param name: The name to give to the ``variable`` in the cell output. This name
                 must be used when pasting this output in other cells.
    :param variable: The object to be inserted into the cell output. Note that the
                     object itself is not stored. Rather, this function inserts the JSON
                     representation of the plot into the cell output, which must then be
                     extracted and shown by the `~myst_nb_bokeh.BokehOutputRenderer`.
    :param display: If ``True``, the plot will be shown in the output of the cell.
                    Useful for sanity checking the output. ``False`` by default.
    """
    mime_prefix = "" if display else MYST_NB_GLUE_PREFIX
    metadata = {"scrapbook": dict(name=name, mime_prefix=mime_prefix, has_bokeh=True)}
    ipy_display(
        {
            mime_prefix
            + JB_BOKEH_MIMETYPE: json.dumps(json_item(variable, name), separators=(",", ":"))
        },
        raw=True,
        metadata=metadata,
    )
    if display:
        script, div = components(variable, wrap_script=False)
        s = Javascript(script, lib=CDN.js_files[0])
        h = HTML(div)
        ipy_display(h, s)


class BokehOutputRenderer(MimeRenderPlugin):
    """MyST-NB plugin that renders the custom Bokeh mimetype.

    See the `MyST-NB docs
    <https://myst-nb.readthedocs.io/en/latest/render/format_code_cells.html#render-output-cutomise>`__
    for further information.
    """  # noqa: F501

    @staticmethod
    def handle_mime(  # noqa: D102
        renderer: NbElementRenderer, data: MimeData, inline: int
    ) -> None | list[nodes.Element]:
        if not inline and data.mime_type == JB_BOKEH_MIMETYPE:
            name = data.output_metadata["scrapbook"]["name"]
            html_node = nodes.raw(text=f'<div id="{name}"></div>', format="html")
            js_text = dedent(
                f"""\
                <script type="text/javascript">
                Bokeh.embed.embed_item(
                    {data.content}
                );
                </script>"""
            )
            js_node = nodes.raw(text=js_text, format="html")

            for i, js_file in enumerate(CDN.js_files):
                renderer.add_js_file(f"bokeh-js-{i}", js_file, kwargs={})
            for i, js_raw in enumerate(CDN.js_raw):
                # Sphinx actually allows None as the first argument to allow a string as
                # the body of the script element. For some reason, the function is not
                # typed this way.
                renderer.add_js_file(f"bokeh-raw-js-{i}", None, kwargs={"body": js_raw})

            return [html_node, js_node]

        return None
