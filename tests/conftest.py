"""Common configuration for tests."""

import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import pytest
from lxml import etree
from lxml.doctestcompare import LHTMLOutputChecker
from sphinx.util.console import nocolor

pytest_plugins = "sphinx.testing.fixtures"

TEST_FILE_DIR = Path(__file__).parent.joinpath("notebooks")


class SphinxFixture:
    """Returned by the ``sphinx_run`` fixture, to run Sphinx, and retrieve aspects of the build."""

    def __init__(self, app, filenames):
        """Construct the class with a Sphinx application and a list of filenames to build."""
        self.app = app
        self.env = app.env
        self.files = [os.path.splitext(ff) for ff in filenames]

        # self.nb_file = nb_file
        # self.nb_name = os.path.splitext(nb_file)[0]

    def build(self):
        """Run the sphinx build."""
        # reset streams before each build
        self.app._status.truncate(0)
        self.app._status.seek(0)
        self.app._warning.truncate(0)
        self.app._warning.seek(0)
        self.app.build()

    def warnings(self):
        """Return the stderr stream of the sphinx build."""
        return self.app._warning.getvalue().strip()


@pytest.fixture()
def sphinx_params(request):
    """Parameterize Sphinx runs.

    Parameters that are specified by 'pytest.mark.sphinx_params'
    are passed to the ``sphinx_run`` fixture::

        @pytest.mark.sphinx_params("name.ipynb", conf={"option": "value"})
        def test_something(sphinx_run):
            ...

    The first file specified here will be set as the master_doc
    """
    markers = request.node.iter_markers("sphinx_params")
    kwargs = {}
    if markers is not None:
        for info in reversed(list(markers)):
            kwargs.update(info.kwargs)
            kwargs["files"] = info.args
    return kwargs


@pytest.fixture()
def sphinx_run(sphinx_params, make_app, tempdir):
    """Set up and run a Sphinx build, in a sandboxed folder.

    The `myst_nb_bokeh` extension is added by default,
    and the first file in sphinx_params/files will be set as the master_doc
    """
    assert len(sphinx_params["files"]) > 0, sphinx_params["files"]
    conf = sphinx_params.get("conf", {})
    buildername = sphinx_params.get("buildername", "html")

    confoverrides = {
        "extensions": ["myst_nb_bokeh"],
        "master_doc": os.path.splitext(sphinx_params["files"][0])[0],
        "exclude_patterns": ["_build"],
        "execution_show_tb": True,
        "myst_enable_extensions": ["colon_fence"],
    }
    confoverrides.update(conf)

    current_dir = os.getcwd()
    base_dir = tempdir
    srcdir = base_dir / "source"
    srcdir.makedirs(exist_ok=True)
    os.chdir(base_dir)
    (srcdir / "conf.py").write_text(
        "# conf overrides (passed directly to sphinx):\n"
        + "\n".join(["# " + ll for ll in json.dumps(confoverrides, indent=2).splitlines()])
        + "\n"
    )

    for nb_file in sphinx_params["files"]:
        nb_path = TEST_FILE_DIR.joinpath(nb_file)
        assert nb_path.exists(), nb_path
        (srcdir / nb_file).parent.makedirs(exist_ok=True)
        (srcdir / nb_file).write_text(nb_path.read_text(encoding="utf8"))

    nocolor()
    app = make_app(buildername=buildername, srcdir=srcdir, confoverrides=confoverrides)

    yield SphinxFixture(app, sphinx_params["files"])

    # reset working directory
    os.chdir(current_dir)


class BokehHTMLChecker(LHTMLOutputChecker):
    """Check the HTML of a Notebook with Bokeh."""

    def __init__(self, *args, **kwargs):  # noqa: D107
        super().__init__(*args, **kwargs)
        self.found_bokehjs = False

    def compare_docs(self, want, got):
        """Compare two HTML documents.

        Similar to lxml.doctestcompare.LHTMLOutputChecker, but raises AssertionErrors with more
        context, instead of returning a Boolean value.
        """
        if not self.tag_compare(want.tag, got.tag):
            raise AssertionError(f"Expected tag: {want.tag}; Obtained tag: {got.tag}")
        if want.tag == "script" and want.text is not None and "Bokeh" in want.text:
            if got.text is None or "Bokeh" not in got.text:
                raise AssertionError(f"Expected text: {want.text!r}; Obtained text: {got.text!r}")
        elif not self.text_compare(want.text, got.text, True):
            raise AssertionError(f"Expected text: {want.text!r}; Obtained text: {got.text!r}")
        if not self.text_compare(want.tail, got.tail, True):
            raise AssertionError(f"Expected tail: {want.tail!r}; Obtained tail: {got.tail!r}")
        if "any" not in want.attrib:
            want_keys = sorted(want.attrib.keys())
            got_keys = sorted(got.attrib.keys())
            assert want_keys == got_keys
            for key in want_keys:
                if key in ("src", "href") and "https" in want.attrib[key]:
                    if self.url_compare(want.attrib[key], got.attrib[key]):
                        self.found_bokehjs = True
                elif not self.text_compare(want.attrib[key], got.attrib[key], False):
                    raise AssertionError(
                        f"Expected value: {want.attrib[key]}; Obtained value: {got.attrib[key]}"
                    )
        if want.text != "..." or len(want):
            want_children = list(want)
            got_children = list(got)
            while want_children or got_children:
                if not want_children:
                    raise AssertionError("Obtained document has more child elements.")
                elif not got_children:
                    raise AssertionError("Expected document has more child elements.")
                want_first = want_children.pop(0)
                got_first = got_children.pop(0)
                self.compare_docs(want_first, got_first)
                if not got_children and want_first.tail == "...":
                    break

    def url_compare(self, want, got):
        """Compare URLs from script and link tags.

        Raises AssertionErrors if there are differences in the parsed URL.
        Returns True if the URL has 'bokeh' in it, otherwise returns False.
        """
        want = urlparse(want)
        got = urlparse(got)
        for attr in ("scheme", "netloc", "query", "params", "fragment"):
            if getattr(want, attr) != getattr(got, attr):
                raise AssertionError(
                    f"Expected value: {getattr(want, attr)}; Obtained value: {getattr(got, attr)}"
                )
        if "bokeh" in got.netloc:
            # Compare path portions separately to allow different versions to compare equal.
            url_re = re.compile(r"(/bokeh/release/bokeh-[\w-]*)\d\.\d\.\d(\.min\.js)")
            want_path = url_re.match(want.path)
            got_path = url_re.match(got.path)
            if want_path is None:
                raise AssertionError(f"Expected output did not match: {want.path}")
            if got_path is None:
                raise AssertionError(f"Obtained output did not match: {got.path}")
            if want_path.groups() != got_path.groups():
                raise AssertionError(f"Expected value: {want.path}; Obtained value: {got.path}")
            return True
        else:
            if want.path != got.path:
                raise AssertionError(f"Expected value: {want.path}; Obtained value: {got.path}")
            return False


@pytest.fixture()
def check_bokeh():
    """Check Bokeh JSON output, which is in non-deterministic order."""

    def _check_bokeh(obtained_filename, expected_filename):
        _html_parser = etree.HTMLParser(recover=True, remove_blank_text=True)

        def html_fromstring(html):
            return etree.fromstring(html, _html_parser)

        obtained_doc = html_fromstring(obtained_filename.read_text())
        expected_doc = html_fromstring(expected_filename.read_text())
        c = BokehHTMLChecker()
        result = c.compare_docs(expected_doc, obtained_doc)
        if not c.found_bokehjs:
            raise AssertionError("Did not find BokehJS scripts in the page head.")
        if not result and result is not None:
            diff = c.collect_diff(expected_doc, obtained_doc, True, 2)
            raise AssertionError(diff)

    return _check_bokeh
