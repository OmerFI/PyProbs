# PyProbs

[![Tests](https://github.com/OmerFI/PyProbs/actions/workflows/tests.yml/badge.svg)](https://github.com/OmerFI/PyProbs/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/pyprobs)](https://pypi.org/project/pyprobs/)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/pyprobs.svg?color=blueviolet)](https://pypi.org/project/pyprobs/)
[![Docs](https://github.com/OmerFI/PyProbs/actions/workflows/docs.yml/badge.svg)](https://omerfi.github.io/PyProbs/)
[![Downloads](https://static.pepy.tech/badge/pyprobs)](https://pepy.tech/project/pyprobs)
[![License](https://img.shields.io/github/license/OmerFI/PyProbs)](https://github.com/OmerFI/PyProbs/blob/main/LICENSE)

Get `True` or `False` from a probability, whether you write it as a float, a percentage or a fraction.

**Documentation**: [https://omerfi.github.io/PyProbs](https://omerfi.github.io/PyProbs/)

**Source Code**: [https://github.com/OmerFI/PyProbs](https://github.com/OmerFI/PyProbs)

---

PyProbs turns a probability into a decision. Ask for `"25%"` and roughly one call in four returns `True`. You can draw
once, draw many times in a single call, or keep an instance around that remembers every result and counts them for you.

The key features are:

- **Any notation**: `0.25`, `"25%"`, `"1/4"` and `"0.25"` all mean the same probability.
- **Quick or tracked**: `Probability.prob()` draws without any setup, while an instance's `iprob()` records a history
  you can count.
- **Typed**: Ships with type hints and is checked with mypy in strict mode.
- **No dependencies**: Pure Python, nothing else to install.

## Installation

PyProbs supports Python 3.11+.

First, [install `uv`](https://docs.astral.sh/uv/getting-started/installation/), and then add PyProbs to your project:

```console
$ uv add pyprobs
```

If you prefer to use `pip`, install it inside a virtual environment:

```console
$ pip install pyprobs
```

## Example

### Draw without setup

```pycon
>>> from pyprobs import Probability as pr
>>> pr.prob(0.5)
False
>>> pr.prob("50%", num=5)
[False, True, False, False, False]
>>> pr.prob(1, 0)  # Several probabilities return one flat list
[True, False]
```

### Keep a history

```pycon
>>> p = pr()
>>> p.iprob("3/4", 0.5, num=2)
[[True, True], [True, False]]
>>> p.history
{'3/4': [True, True], 0.5: [True, False]}
>>> p.count_values("all")
{True: 3, False: 1}
```

### Set a constant

When most of your calls use the same probability, set it once and call `iprob()` without arguments. Passing
`mutable=False` locks it, so a later `set_constant()` raises an error.

```pycon
>>> p.set_constant("1/1000", mutable=False)
>>> p.iprob()
False
>>> p.get()
{'constant': '1/1000', 'mutable': False}
```

## Supported notations

| Form       | Examples                 |
|------------|--------------------------|
| int        | `0`, `1`                 |
| float      | `0.25`, `1e-05`          |
| Percentage | `"25%"`, `"%12.5"`       |
| Fraction   | `"1/4"`, `" 3 / 7 "`     |
| Number     | `"0.25"`                 |

A value outside the 0–1 range raises `ProbabilityRangeError`, and a str that cannot be read as a probability raises
`ProbabilityTypeError`.

## API

All methods live on the `Probability` class. `prob()` can be called on the class itself, the rest need an instance.

| Method                                  | What it does                                                                |
|-----------------------------------------|-----------------------------------------------------------------------------|
| `prob(*args, num=1)`                    | Draws `num` results for each probability.                                   |
| `iprob(*args, num=1)`                   | Same as `prob()`, but records the results in `history` and uses the constant when no args are given. |
| `set_constant(constant, mutable=True)`  | Sets the probability `iprob()` uses when called without args.               |
| `get(how="constant&mutable")`           | Returns the constant, the mutable flag or both.                             |
| `count_values(which="last")`            | Counts `True` and `False` results of the last `iprob()` call, or of the whole history with `"all"`. |
| `clear()`                               | Empties the history.                                                        |

The [User Guide](https://omerfi.github.io/PyProbs/src/user-guide.html) walks through all of them, and the
[API Reference](https://omerfi.github.io/PyProbs/src/api-documentation.html) lists every parameter and exception.

## Contributing

The project uses [uv](https://docs.astral.sh/uv/) for development. After cloning the repository, install the
dependencies and the pre-commit hooks, then run the tests:

```console
$ uv sync
$ uv run pre-commit install
$ uv run pytest
```

Pre-commit runs ruff on every commit. Type checking is run separately with `uv run mypy`.

The tests also run every example in this README and in the docs, so their outputs stay true. To preview the docs
while you edit them, run `uv run --group docs zensical serve` and open http://localhost:8000.

## License

This project is licensed under the terms of the [MIT license](https://github.com/OmerFI/PyProbs/blob/main/LICENSE).
