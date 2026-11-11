---
icon: lucide/book-open
---

# User Guide

PyProbs answers one question: given a probability, did the event happen? This guide walks through the ways to ask
it, from a single call to an instance that keeps score.

## Drawing outcomes

`Probability.prob()` is a static method, so you can call it straight on the class. Each call draws a new outcome,
which is `True` with the probability you give:

```pycon
>>> from pyprobs import Probability as pr
>>> pr.prob(0.5)
False
```

Pass `num` to draw several outcomes at once. They come back as a list:

```pycon
>>> pr.prob("50%", num=8)
[False, True, False, False, False, False, False, False]
```

When you pass more than one probability, the outcomes of all of them are returned in one flat list, in order:

```pycon
>>> pr.prob(1, 0, num=2)
[True, True, False, False]
```

!!! note "`0` and `1` are exact"

    A probability of `0` never comes out `True` and `1` always does, so they are safe to use as switches.

## Writing probabilities

Every function accepts the same forms, so write a probability whichever way reads best where you use it:

| Form       | Examples             | Notes                                                 |
|------------|----------------------|-------------------------------------------------------|
| int        | `0`, `1`             | Only `0` and `1` are valid probabilities.             |
| float      | `0.25`, `1e-05`      |                                                       |
| Percentage | `"25%"`, `"%12.5"`   | The sign can be on either side, decimals are fine.    |
| Fraction   | `"1/4"`, `" 3 / 7 "` | Spaces around the numbers are ignored.                |
| Number     | `"0.25"`             | A number written as a str works like the float.       |

!!! note "Probabilities are exact"

    PyProbs keeps every probability as an exact fraction, so `"3/7"` comes out `True` with a chance of exactly 3 in
    7. A float counts as the decimal it prints as, so `0.1` is exactly one in ten. One third has no such decimal, so
    write it as `"1/3"`: the float `1/3` is already rounded to `0.3333333333333333` before PyProbs sees it.

A value outside the 0 to 1 range raises `ProbabilityRangeError`:

```pycon
>>> pr.prob("150%")
Traceback (most recent call last):
  ...
pyprobs.exceptions.ProbabilityRangeError: The probability of an event must be between 0 and 1.
```

A value that cannot be read as a probability at all raises `ProbabilityTypeError`:

```pycon
>>> pr.prob("half")
Traceback (most recent call last):
  ...
pyprobs.exceptions.ProbabilityTypeError: 'half' is not a valid probability. Use a percentage ('25%'), a fraction ('1/4') or a number ('0.25').
```

## Keeping a history

Create an instance when you want to keep track of what was drawn. Its `iprob()` method works like `prob()`, and also
records every outcome in `history`, under the probability it was drawn for:

```pycon
>>> p = pr()
>>> p.iprob("3/4", 0.5, num=2)
[[True, True], [True, False]]
>>> p.history
{'3/4': [True, True], 0.5: [True, False]}
```

Unlike `prob()`, `iprob()` keeps the outcomes of each probability apart:

| Call                    | Returns                                     |
|-------------------------|---------------------------------------------|
| `p.iprob(0.5)`          | a bool                                      |
| `p.iprob(0.5, num=3)`   | a list of bools                             |
| `p.iprob(0.5, "25%")`   | one list per probability, like `[[True], [False]]` |

Outcomes for the same probability add up across calls. A fraction or percentage is stored without the spaces around
it, so `" 3 / 4 "` and `"3/4"` share one entry:

```pycon
>>> p.iprob(" 3 / 4 ", num=4)
[True, True, True, False]
>>> p.history["3/4"]
[True, True, True, True, True, False]
```

`count_values()` counts the outcomes of the last `iprob()` call, or of the whole history with `"all"`:

```pycon
>>> p.count_values()
{True: 3, False: 1}
>>> p.count_values("all")
{True: 6, False: 2}
```

`clear()` empties the history:

```pycon
>>> p.clear()
>>> p.history
{}
```

## Setting a constant

When an instance always draws with the same probability, set it once with `set_constant()` and call `iprob()` without
arguments. A probability you pass to `iprob()` still takes precedence:

```pycon
>>> coin = pr()
>>> coin.set_constant("50%")
>>> coin.iprob(num=4)
[True, False, False, False]
>>> coin.iprob(0)
False
```

Pass `mutable=False` to lock the constant. Any later attempt to change it raises `ImmutableConstantVariableError`:

```pycon
>>> d20 = pr()
>>> d20.set_constant("1/20", mutable=False)
>>> d20.set_constant("1/2")
Traceback (most recent call last):
  ...
pyprobs.exceptions.ImmutableConstantVariableError: The mutable parameter has been set False before. You cannot set a constant again.
```

`get()` returns the constant and the mutable flag, together or one at a time:

```pycon
>>> d20.get()
{'constant': '1/20', 'mutable': False}
>>> d20.get("constant")
'1/20'
>>> d20.get("mutable")
False
```

## Combining instances

Instances with a constant work with a few Python operators. `+` returns a new instance whose constant is the sum of
both, capped at `1`, and `float()` gives the constant as a number:

```pycon
>>> rolls_one = pr()
>>> rolls_one.set_constant("1/6")
>>> rolls_two = pr()
>>> rolls_two.set_constant("1/6")
>>> rolls_one_or_two = rolls_one + rolls_two
>>> float(rolls_one_or_two)
0.3333333333333333
```

!!! warning "Adding is only right for events that exclude each other"

    The sum is the chance that either event happens only when they cannot both happen, like two faces of the same
    die. For independent events, such as rain on two different days, the real chance is lower than the sum.

`==` compares the constants as they were written, together with the mutable flag. So `"50%"` and `0.5` are not equal,
even though they describe the same chance:

```pycon
>>> half = pr()
>>> half.set_constant("50%")
>>> also_half = pr()
>>> also_half.set_constant(0.5)
>>> half == also_half
False
```

## Handling errors

Every exception PyProbs raises derives from `ProbabilityError`, so one `except` clause covers them all:

```pycon
>>> from pyprobs.exceptions import ProbabilityError
>>> try:
...     pr.prob("lots")
... except ProbabilityError as error:
...     print(f"Could not draw: {error}")
Could not draw: 'lots' is not a valid probability. Use a percentage ('25%'), a fraction ('1/4') or a number ('0.25').
```

| Exception                        | Raised when                                                              |
|----------------------------------|--------------------------------------------------------------------------|
| `ProbabilityRangeError`          | A probability is outside the 0 to 1 range.                               |
| `ProbabilityTypeError`           | A probability is not an int, float or str, or cannot be read as one.     |
| `NumError`                       | `num` is less than one or not a whole number.                            |
| `NotGivenValueError`             | No probability is given, and for `iprob()` no constant is set either.    |
| `ConstantError`                  | A constant is invalid, or an operation needs a constant that is not set. |
| `ImmutableConstantVariableError` | A locked constant is changed.                                            |
| `NotUsedError`                   | `count_values()` is asked for the last outcomes before any `iprob()`.    |
| `InvalidParameterValue`          | `which` or `how` has an unsupported value.                               |

## Reproducible results

PyProbs draws with Python's [`random`](https://docs.python.org/3/library/random.html) module, so seeding it makes the
outcomes repeat. This is handy in tests and in simulations you want to rerun:

```pycon
>>> import random
>>> random.seed(42)
>>> pr.prob("50%", num=5)
[True, True, False, True, True]
>>> random.seed(42)
>>> pr.prob("50%", num=5)
[True, True, False, True, True]
```

!!! danger "Not for security"

    The `random` module is predictable by design. For tokens, passwords or any choice an attacker must not be able to
    guess, use Python's [`secrets`](https://docs.python.org/3/library/secrets.html) module instead.
