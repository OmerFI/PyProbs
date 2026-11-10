---
icon: lucide/flask-conical
---

# Examples

Short recipes for things people use PyProbs for. Each one assumes this import:

```pycon
>>> from pyprobs import Probability as pr
```

## Loot drops in a game

Check the rarest reward first. Because the checks run in order, the ring below has a 30% chance only when the sword
did not drop:

```pycon
>>> def open_chest():
...     if pr.prob("5%"):
...         return "legendary sword"
...     if pr.prob("30%"):
...         return "silver ring"
...     return "gold coins"
>>> for _ in range(5):
...     print(open_chest())
gold coins
silver ring
gold coins
gold coins
gold coins
```

## Checking a probability by simulation

Draw many outcomes and look at the share that came out `True`. `sum()` counts the `True` values, so the share gets
closer to the probability as the number of draws grows:

```pycon
>>> outcomes = pr.prob("1/3", num=100_000)
>>> sum(outcomes) / len(outcomes)
0.33453
```

## Sampling a fraction of items

Keep roughly one item in ten, for example to log the details of a sample of requests:

```pycon
>>> sampled = []
>>> for request_id in range(1, 31):
...     if pr.prob("10%"):
...         sampled.append(request_id)
>>> sampled
[19, 20]
```

## Free throws with a fixed success rate

An instance with a constant remembers the rate, and its history keeps the score. Ten throws are few, so the count
can stray quite far from 72%:

```pycon
>>> player = pr()
>>> player.set_constant("72%")
>>> player.iprob(num=10)
[False, True, True, False, True, True, False, True, False, False]
>>> player.count_values()
{True: 5, False: 5}
>>> player.iprob(num=10)
[True, True, False, False, False, True, True, True, False, True]
>>> player.count_values("all")
{True: 11, False: 9}
```

## Stable outcomes in tests

Seed the `random` module before each test, and every run draws the same outcomes. With pytest, an autouse fixture
does it for all tests in a module:

```python
import random

import pytest


@pytest.fixture(autouse=True)
def seed_random():
    random.seed(1234)
```
