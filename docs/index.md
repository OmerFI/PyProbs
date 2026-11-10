---
icon: lucide/house
hide:
  - navigation
  - toc
---

<div class="pyprobs-hero" markdown>

# PyProbs

<p class="pyprobs-tagline">Get <code>True</code> or <code>False</code> from a probability, whether you write it as a
float, a percentage or a fraction.</p>

[Get started](src/installation.md){ .md-button .md-button--primary }
[User Guide](src/user-guide.md){ .md-button }

</div>

```console
$ uv add pyprobs
```

PyProbs turns a probability into a decision. Ask for `"25%"` and roughly one call in four returns `True`. You can draw
once, draw many times in a single call, or keep an instance around that remembers every result and counts them for you.

<div class="grid cards pyprobs-features" markdown>

-   :lucide-percent:{ .lg .middle } __Any notation__

    ---

    `0.25`, `"25%"`, `"1/4"` and `"0.25"` all mean the same probability.

-   :lucide-history:{ .lg .middle } __Quick or tracked__

    ---

    `Probability.prob()` draws without any setup, while an instance's `iprob()` records a history you can count.

-   :lucide-shield-check:{ .lg .middle } __Typed__

    ---

    Ships with type hints and is checked with mypy in strict mode.

-   :lucide-package:{ .lg .middle } __No dependencies__

    ---

    Pure Python, nothing else to install.

</div>

## A quick look

```pycon
>>> from pyprobs import Probability as pr
>>> pr.prob("50%", num=5)
[False, False, True, True, False]
>>> p = pr()
>>> p.iprob("3/4", 0.5, num=2)
[[True, False], [True, True]]
>>> p.count_values("all")
{True: 3, False: 1}
```
