import random
import re
from fractions import Fraction
from typing import Literal, TypedDict, overload

from . import exceptions

ProbabilityValue = int | float | str
"""A probability written as an int (`0`, `1`), a float (`0.25`) or a str (`"25%"`, `"1/4"`, `"0.25"`)."""

UNSET_CONSTANT = "unset"

# Fraction turns the exponent of '1e-1000000000' into a denominator with that many digits, so the exponent gets the
# same 4300 cap that Python puts on the digits of an int str.
MAX_EXPONENT = 4300


class ConstantSettings(TypedDict):
    """
    The constant and mutable values returned by `Probability.get()`.

    Attributes:
        constant: The constant as it was given to `set_constant()`, or `"unset"` when no constant is set.
        mutable: Whether the constant can still be changed.
    """

    constant: ProbabilityValue
    mutable: bool


def _to_probability(value: ProbabilityValue) -> Fraction:
    """
    Convert a probability given by the user into an exact fraction between 0 and 1.

    Every public function accepts the same three forms, so they all pass through here: an int (0 or 1), a float
    (0.25, 1e-05) or a str. A str can be a percentage ('25%', '%25', '12.5%'), a fraction ('1/4', ' 1 / 4 ') or a
    plain number ('0.25'). Keeping the probability as a Fraction instead of a float lets ``_draw()`` give '3/7' a
    chance of exactly 3/7, rather than of the float closest to it.

    Args:
        value: The probability in one of the forms above.

    Raises:
        ProbabilityTypeError: When the value is not an int, float or str, or the str cannot be read as a probability.
        ProbabilityRangeError: When the value is outside the 0-1 range, e.g. 2, '150%' or '3/2'.

    Returns:
        Fraction: The probability as a fraction between 0 and 1.
    """
    if isinstance(value, str):
        probability = _str_to_probability(value)
    elif isinstance(value, float):
        # repr gives the decimal the float prints as (0.1), while Fraction(0.1) gives its binary value (0.1000…0555).
        probability = _str_to_probability(repr(value))
    elif isinstance(value, int):
        probability = Fraction(value)
    else:
        raise exceptions.ProbabilityTypeError("The probability must be int, float, or str.")

    if not 0 <= probability <= 1:
        raise exceptions.ProbabilityRangeError("The probability of an event must be between 0 and 1.")

    return probability


def _str_to_probability(value: str) -> Fraction:
    """Read a percentage, fraction or plain number str as an exact Fraction."""
    if "%" in value and "/" in value:
        raise exceptions.ProbabilityTypeError("Given str value must contain either '%' or '/', not both.")

    try:
        if "%" in value:
            probability = _to_fraction(value.strip().strip("%")) / 100
        elif "/" in value:
            numerator, denominator = value.split("/")
            probability = _to_fraction(numerator) / _to_fraction(denominator)
        else:
            probability = _to_fraction(value)
    except (ValueError, ZeroDivisionError):
        raise exceptions.ProbabilityTypeError(
            f"{value!r} is not a valid probability. Use a percentage ('25%'), a fraction ('1/4') or a number ('0.25')."
        ) from None

    return probability


def _to_fraction(text: str) -> Fraction:
    """Read a number str as a Fraction, refusing an exponent large enough to make building it hang."""
    exponent = re.search(r"e([+-]?[\d_]+)", text, re.IGNORECASE)
    if exponent is not None and abs(int(exponent[1])) > MAX_EXPONENT:
        raise exceptions.ProbabilityTypeError(f"{text.strip()!r} has an exponent beyond {MAX_EXPONENT}.")

    number = Fraction(text)
    return number


def _normalize(value: ProbabilityValue) -> ProbabilityValue:
    """Remove the spaces around '%' and '/' so that ' 3 / 7 ' and '3/7' share one history key."""
    if not isinstance(value, str):
        return value

    normalized = value.strip()
    for separator in ["/", "%"]:
        normalized = separator.join(part.strip() for part in normalized.split(separator))

    return normalized


def _validate_num(num: float) -> int:
    """Return num as an int, rejecting values below one and floats with a fractional part."""
    if not float(num).is_integer():
        raise exceptions.NumError("The num parameter must be int and at least one.")

    if num < 1:
        raise exceptions.NumError("The num parameter must be at least one.")

    return int(num)


def _draw(probability: Fraction, num: int) -> list[bool]:
    """Draw num independent outcomes, each True when a whole number below the denominator falls under the numerator."""
    outcomes: list[bool] = []
    for _ in range(num):
        outcomes.append(random.randrange(probability.denominator) < probability.numerator)

    return outcomes


class Probability:
    """
    Turn probabilities into `True` or `False` outcomes.

    `prob()` is a static method, so it can be called on the class itself without any setup. The other methods work on
    an instance, which keeps a history of the outcomes it draws and can hold a constant probability.

    Attributes:
        history: The outcomes drawn by `iprob()`, keyed by the probability they were drawn for.

    Examples:
        >>> from pyprobs import Probability as pr
        >>> pr.prob("25%")
        False
        >>> p = pr()
        >>> p.iprob("3/7", 0.25, num=2)
        [[False, False], [True, False]]
        >>> p.history
        {'3/7': [False, False], 0.25: [True, False]}
        >>> p.count_values("all")
        {True: 1, False: 3}
    """

    def __init__(self) -> None:
        self._mutable = True
        self._constant: ProbabilityValue = UNSET_CONSTANT
        self._last_values: list[bool] = []
        self.history: dict[ProbabilityValue, list[bool]] = {}

    def __str__(self) -> str:
        return f"Probability(_constant='{self._constant}', _mutable={self._mutable})"

    def __float__(self) -> float:
        if self._constant == UNSET_CONSTANT:
            raise exceptions.ConstantError("The constant must be set before.")

        return float(_to_probability(self._constant))

    def __int__(self) -> int:
        return int(float(self))

    def __add__(self, other: object) -> "Probability":
        if not isinstance(other, Probability):
            return NotImplemented

        if self._constant == UNSET_CONSTANT or other._constant == UNSET_CONSTANT:
            raise exceptions.ConstantError("The objects' constants must be set before.")

        total = _to_probability(self._constant) + _to_probability(other._constant)

        result = Probability()
        result.set_constant(min(float(total), 1), self._mutable or other._mutable)
        return result

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Probability):
            return NotImplemented

        return self.get() == other.get()

    @staticmethod
    def prob(*args: ProbabilityValue, num: int = 1) -> bool | list[bool]:
        """
        Draw `True` or `False` outcomes for one or more probabilities.

        Each outcome is `True` with the given probability, so `"25%"` gives `True` about one time in four. A
        probability of `0` always gives `False` and `1` always gives `True`. The chance is exact, so write a
        probability like one third as `"1/3"`: the float `1/3` is already rounded before it reaches PyProbs.

        Args:
            *args: The probabilities to draw for, written as an int (`0`, `1`), a float (`0.25`, `1e-05`) or a str
                (`"25%"`, `"%12.5"`, `"1/4"`, `"0.25"`).
            num: How many outcomes to draw for each probability.

        Raises:
            NotGivenValueError: When no probability is given.
            NumError: When `num` is less than one or not a whole number.
            ProbabilityTypeError: When a probability is not an int, float or str, or a str cannot be read as one.
            ProbabilityRangeError: When a probability is not between 0 and 1.

        Returns:
            A bool when a single probability is drawn once, otherwise a flat list of every outcome in order.

        Examples:
            >>> from pyprobs import Probability as pr
            >>> pr.prob(0.5)
            False
            >>> pr.prob("25%", num=5)
            [False, True, False, False, False]
            >>> pr.prob(1, 0, num=2)
            [True, True, False, False]
        """
        if not args:
            raise exceptions.NotGivenValueError("No value was given.")

        num = _validate_num(num)

        probabilities: list[Fraction] = []
        for arg in args:
            probabilities.append(_to_probability(arg))

        values: list[bool] = []
        for probability in probabilities:
            values.extend(_draw(probability, num))

        if len(values) == 1:
            return values[0]

        return values

    def iprob(self, *args: ProbabilityValue, num: int = 1) -> bool | list[bool] | list[list[bool]]:
        """
        Draw outcomes like `prob()` and record them in the instance's history.

        Each outcome is stored in `history` under the probability it was drawn for. When no probability is given, the
        constant set with `set_constant()` is used.

        Args:
            *args: The probabilities to draw for, in any of the forms that `prob()` accepts.
            num: How many outcomes to draw for each probability.

        Raises:
            NotGivenValueError: When no probability is given and no constant is set.
            NumError: When `num` is less than one or not a whole number.
            ProbabilityTypeError: When a probability is not an int, float or str, or a str cannot be read as one.
            ProbabilityRangeError: When a probability is not between 0 and 1.

        Returns:
            For a single probability, a bool when `num` is 1 and a list of bools otherwise. For several
            probabilities, one list of outcomes per probability.

        Examples:
            >>> from pyprobs import Probability as pr
            >>> p = pr()
            >>> p.iprob(0.2)
            False
            >>> p.iprob("60%", 0.15, num=2)
            [[False, True], [False, False]]
            >>> p.history
            {0.2: [False], '60%': [False, True], 0.15: [False, False]}

            Without arguments, `iprob()` draws with the constant:

            >>> p.set_constant(0.5)
            >>> p.iprob(num=3)
            [False, False, False]
        """
        if args:
            values = list(args)
        elif self._constant == UNSET_CONSTANT:
            raise exceptions.NotGivenValueError("No value was given and no constant was set.")
        else:
            values = [self._constant]

        num = _validate_num(num)

        probabilities: list[Fraction] = []
        for value in values:
            probabilities.append(_to_probability(value))

        results: list[list[bool]] = []
        self._last_values = []
        for value, probability in zip(values, probabilities):
            outcomes = _draw(probability, num)

            key = _normalize(value)
            if key not in self.history:
                self.history[key] = []
            self.history[key].extend(outcomes)

            self._last_values.extend(outcomes)
            results.append(outcomes)

        if len(results) > 1:
            return results

        if num > 1:
            return results[0]

        return results[0][0]

    def set_constant(self, constant: ProbabilityValue, mutable: bool = True) -> None:
        """
        Set the probability that `iprob()` draws with when it is called without arguments.

        Probabilities passed to `iprob()` still take precedence over the constant. With `mutable=False` the constant is
        locked, and any later call to this method raises `ImmutableConstantVariableError`.

        Args:
            constant: The probability, in any of the forms that `prob()` accepts.
            mutable: Whether the constant can be changed again later.

        Raises:
            ConstantError: When the constant is not a valid probability between 0 and 1.
            ImmutableConstantVariableError: When the constant was locked by an earlier call with `mutable=False`.

        Examples:
            >>> from pyprobs import Probability as pr
            >>> p = pr()
            >>> p.set_constant("1/1000", mutable=False)
            >>> p.get()
            {'constant': '1/1000', 'mutable': False}
        """
        try:
            _to_probability(constant)
        except exceptions.ProbabilityError as error:
            raise exceptions.ConstantError(f"The constant parameter is not a valid probability. {error}") from error

        if not self._mutable:
            raise exceptions.ImmutableConstantVariableError(
                "The mutable parameter has been set False before. You cannot set a constant again."
            )

        self._constant = constant
        self._mutable = mutable

    def clear(self) -> None:
        """
        Remove every outcome from the history.

        Examples:
            >>> from pyprobs import Probability as pr
            >>> p = pr()
            >>> p.iprob(1, num=2)
            [True, True]
            >>> p.clear()
            >>> p.history
            {}
        """
        self.history.clear()

    def count_values(self, which: str = "last") -> dict[bool, int]:
        """
        Count the `True` and `False` outcomes drawn by `iprob()`.

        Args:
            which: `"last"` counts the outcomes of the most recent `iprob()` call, and `"all"` counts the whole
                history.

        Raises:
            InvalidParameterValue: When `which` is not `"last"` or `"all"`.
            NotUsedError: When `which` is `"last"` and `iprob()` has not been called yet.

        Returns:
            The number of `True` outcomes under the `True` key and of `False` outcomes under the `False` key.

        Examples:
            >>> from pyprobs import Probability as pr
            >>> p = pr()
            >>> p.iprob(1, 0, num=2)
            [[True, True], [False, False]]
            >>> p.iprob(1)
            True
            >>> p.count_values()
            {True: 1, False: 0}
            >>> p.count_values("all")
            {True: 3, False: 2}
        """
        if which not in ["all", "last"]:
            raise exceptions.InvalidParameterValue("The which parameter can be only 'all' or 'last'.")

        if which == "all":
            values: list[bool] = []
            for outcomes in self.history.values():
                values.extend(outcomes)
        elif self._last_values:
            values = self._last_values
        else:
            raise exceptions.NotUsedError("iprob function must be used at least 1 time before.")

        true_count = values.count(True)
        return {
            True: true_count,
            False: len(values) - true_count,
        }

    @overload
    def get(self, how: Literal["constant&mutable", "mutable&constant"] = ...) -> ConstantSettings: ...

    @overload
    def get(self, how: Literal["constant"]) -> ProbabilityValue: ...

    @overload
    def get(self, how: Literal["mutable"]) -> bool: ...

    # Fallback for a str variable whose value is only known at runtime.
    @overload
    def get(self, how: str) -> ConstantSettings | ProbabilityValue: ...

    def get(self, how: str = "constant&mutable") -> ConstantSettings | ProbabilityValue:
        """
        Return the constant, the mutable flag or both.

        Args:
            how: `"constant&mutable"` and `"mutable&constant"` return both values in a dict, with the keys in that
                order. `"constant"` and `"mutable"` return only that value.

        Raises:
            InvalidParameterValue: When `how` is not one of the four values above.

        Returns:
            A `ConstantSettings` dict, the constant or the mutable flag, depending on `how`. The constant is
            `"unset"` until `set_constant()` is called.

        Examples:
            >>> from pyprobs import Probability as pr
            >>> p = pr()
            >>> p.set_constant("25%")
            >>> p.get()
            {'constant': '25%', 'mutable': True}
            >>> p.get("constant")
            '25%'
            >>> p.get("mutable")
            True
        """
        if how == "constant&mutable":
            return {"constant": self._constant, "mutable": self._mutable}
        elif how == "mutable&constant":
            return {"mutable": self._mutable, "constant": self._constant}
        elif how == "constant":
            return self._constant
        elif how == "mutable":
            return self._mutable
        else:
            raise exceptions.InvalidParameterValue(
                "The how parameter can be only 'constant&mutable', 'mutable&constant', 'constant' or 'mutable'."
            )
