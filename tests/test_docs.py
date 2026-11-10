import doctest
import random
import re
import textwrap
from pathlib import Path

import pytest

import pyprobs.probability

ROOT = Path(__file__).parent.parent
PYCON_BLOCK = re.compile(r"^( *)```pycon\n(.*?)^\1```", re.MULTILINE | re.DOTALL)
# Every example starts from the same seed, so the outputs shown in the docs are the ones these tests produce.
SEED = 0


def markdown_doctests() -> list[doctest.DocTest]:
    """
    Turn the `pycon` blocks of each Markdown file into one doctest.

    The blocks of a page are joined in order, so a later block can use the names an earlier one defined, just like a
    reader following the page in a Python session.
    """
    parser = doctest.DocTestParser()
    paths = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]

    tests: list[doctest.DocTest] = []
    for path in paths:
        blocks: list[str] = []
        for _, block in PYCON_BLOCK.findall(path.read_text()):
            blocks.append(textwrap.dedent(block))

        if not blocks:
            continue

        name = path.relative_to(ROOT).as_posix()
        tests.append(parser.get_doctest("\n".join(blocks), {}, name, str(path), 0))

    return tests


def docstring_doctests() -> list[doctest.DocTest]:
    """Collect the examples in the docstrings of the public module."""
    tests: list[doctest.DocTest] = []
    for test in doctest.DocTestFinder().find(pyprobs.probability):
        if test.examples:
            tests.append(test)

    return tests


@pytest.mark.parametrize("test", markdown_doctests() + docstring_doctests(), ids=lambda test: test.name)
def test_documentation_examples(test: doctest.DocTest) -> None:
    random.seed(SEED)
    runner = doctest.DocTestRunner()
    report: list[str] = []
    runner.run(test, out=report.append)

    assert runner.failures == 0, "".join(report)
