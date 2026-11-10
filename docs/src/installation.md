# Installation

PyProbs supports Python 3.11 and newer, and has no dependencies.

=== "uv"

    ```console
    $ uv add pyprobs
    ```

    New to uv? Follow its [installation guide](https://docs.astral.sh/uv/getting-started/installation/) first.

=== "pip"

    ```console
    $ pip install pyprobs
    ```

    Run it inside a [virtual environment](https://docs.python.org/3/library/venv.html), so PyProbs is installed for
    your project rather than for the whole system.

## Unreleased changes

To try changes that are not on [PyPI](https://pypi.org/project/pyprobs/) yet, install PyProbs straight from
[GitHub](https://github.com/OmerFI/PyProbs):

=== "uv"

    ```console
    $ uv add git+https://github.com/OmerFI/PyProbs
    ```

=== "pip"

    ```console
    $ pip install git+https://github.com/OmerFI/PyProbs
    ```

## Check the installation

A probability of `1` always comes out `True`, which makes for a quick check:

```pycon
>>> from pyprobs import Probability as pr
>>> pr.prob(1)
True
```

Head over to the [User Guide](user-guide.md) to see what else it can do.
