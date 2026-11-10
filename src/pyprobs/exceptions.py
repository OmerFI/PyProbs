"""
Exceptions raised by PyProbs.

Every exception derives from `ProbabilityError`, so catching it handles any of them.
"""


class ProbabilityError(Exception):
    """Base class of every exception that PyProbs raises."""


class ProbabilityRangeError(ProbabilityError):
    """A probability is outside the 0 to 1 range, like `2`, `"150%"` or `"3/2"`."""


class ProbabilityTypeError(ProbabilityError):
    """A probability is not an int, float or str, or a str cannot be read as one, like `"abc"` or `"1/0"`."""


class NumError(ProbabilityError):
    """The `num` argument is less than one or not a whole number."""


class NotGivenValueError(ProbabilityError):
    """No probability was given, and for `iprob()` no constant was set either."""


class NotUsedError(ProbabilityError):
    """`count_values()` was asked for the last outcomes before `iprob()` was ever called."""


class ImmutableConstantVariableError(ProbabilityError):
    """`set_constant()` was called after the constant had been locked with `mutable=False`."""


class ConstantError(ProbabilityError):
    """The constant is not a valid probability, or an operation needs a constant that was never set."""


class InvalidParameterValue(ProbabilityError):
    """An option has an unsupported value, like `which` in `count_values()` or `how` in `get()`."""
