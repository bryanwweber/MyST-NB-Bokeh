"""Tests for `myst_nb_bokeh` package."""

import pytest
from bokeh.plotting import figure
from IPython.core.displaypub import DisplayPublisher
from IPython.core.interactiveshell import InteractiveShell
from myst_nb.ext.glue import GLUE_PREFIX as MYST_NB_GLUE_PREFIX

import myst_nb_bokeh


@pytest.mark.sphinx_params("bokeh.ipynb", conf={"jupyter_execute_notebooks": "force"})
def test_bokeh_notebook(sphinx_run, file_regression, check_bokeh):
    """Test that Bokeh included in a Notebook has the JSON in the output HTML."""
    sphinx_run.build()
    assert sphinx_run.warnings() == ""
    name = sphinx_run.files[0][0]
    _path = sphinx_run.app.outdir / (name + ".html")
    file_regression.check(
        _path.read_text(), check_fn=check_bokeh, extension=".html", encoding="utf8"
    )


class MockDisplayPublisher(DisplayPublisher):
    """Mock the IPython DisplayPublisher class for testing."""

    def __init__(self, *args, **kwargs):
        """Arguments are passed to the superclass."""
        super().__init__(*args, **kwargs)
        self.publish_calls = []

    def publish(self, data, **kwargs):
        """Publish the data.

        Called by the IPython.display machinery.
        """
        kwargs["data"] = data
        self.publish_calls.append(kwargs)


@pytest.fixture()
def mock_ipython():
    """Mock an IPython InteractiveShell for testing."""
    shell = InteractiveShell.instance()  # type: InteractiveShell
    shell.display_pub = MockDisplayPublisher()
    yield shell.display_pub
    InteractiveShell.clear_instance()


def test_glue_bokeh_no_display(mock_ipython):
    """Test gluing a Bokeh figure without displaying it.

    The main difference from a displayed figure is the mime_prefix in the metadata.
    """
    p = figure()
    p.circle(list(range(1, 10)), list(range(1, 10)))
    myst_nb_bokeh.glue_bokeh("a", p)
    obtained = mock_ipython.publish_calls[0]
    assert MYST_NB_GLUE_PREFIX + myst_nb_bokeh.JB_BOKEH_MIMETYPE in obtained["data"].keys()
    scrapbook = obtained["metadata"]["scrapbook"]
    assert "mime_prefix" in scrapbook and scrapbook["mime_prefix"] == MYST_NB_GLUE_PREFIX
    assert "name" in scrapbook and scrapbook["name"] == "a"


def test_glue_bokeh_display(mock_ipython):
    """Test gluing a Bokeh figure while displaying it.

    The main difference from a non-displayed figure is the mime_prefix in the metadata,
    and the addition of an HTML and JavaScript output.
    """
    p = figure()
    p.circle(list(range(1, 10)), list(range(1, 10)))
    myst_nb_bokeh.glue_bokeh("a", p, display=True)
    assert len(mock_ipython.publish_calls) == 3
    obtained_json = mock_ipython.publish_calls[0]
    assert myst_nb_bokeh.JB_BOKEH_MIMETYPE in obtained_json["data"].keys()
    scrapbook = obtained_json["metadata"]["scrapbook"]
    assert "mime_prefix" in scrapbook and not scrapbook["mime_prefix"]
    assert "name" in scrapbook and scrapbook["name"] == "a"
    obtained_html = mock_ipython.publish_calls[1]
    assert "text/html" in obtained_html["data"].keys()
    obtained_js = mock_ipython.publish_calls[2]
    assert "application/javascript" in obtained_js["data"].keys()
