import random
from typing import Literal, TypedDict, overload

from . import exceptions

ProbabilityValue = int | float | str

UNSET_CONSTANT = "unset"


class ConstantSettings(TypedDict):
    """The constant and mutable values returned by ``Probability.get()``."""

    constant: ProbabilityValue
    mutable: bool


def _to_probability(value: ProbabilityValue) -> float:
    """
    Convert a probability given by the user into a float between 0 and 1.

    Every public function accepts the same three forms, so they all pass through here: an int (0 or 1), a float
    (0.25, 1e-05) or a str. A str can be a percentage ('25%', '%25', '12.5%'), a fraction ('1/4', ' 1 / 4 ') or a
    plain number ('0.25'). Converting to float first lets one comparison against ``random.random()`` decide the
    outcome, whatever form the probability was written in.

    Args:
        value: The probability in one of the forms above.

    Raises:
        ProbabilityTypeError: When the value is not an int, float or str, or the str cannot be read as a probability.
        ProbabilityRangeError: When the value is outside the 0-1 range, e.g. 2, '150%' or '3/2'.

    Returns:
        float: The probability as a float between 0 and 1.
    """
    if isinstance(value, str):
        probability = _str_to_probability(value)
    elif isinstance(value, (int, float)):
        probability = float(value)
    else:
        raise exceptions.ProbabilityTypeError("The probability must be int, float, or str.")

    if not 0 <= probability <= 1:
        raise exceptions.ProbabilityRangeError("The probability of an event must be between 0 and 1.")

    return probability


def _str_to_probability(value: str) -> float:
    """Read a percentage, fraction or plain number str as a float."""
    if "%" in value and "/" in value:
        raise exceptions.ProbabilityTypeError("Given str value must contain either '%' or '/', not both.")

    try:
        if "%" in value:
            probability = float(value.strip().strip("%")) / 100
        elif "/" in value:
            numerator, denominator = value.split("/")
            probability = float(numerator) / float(denominator)
        else:
            probability = float(value)
    except (ValueError, ZeroDivisionError):
        raise exceptions.ProbabilityTypeError(
            f"{value!r} is not a valid probability. Use a percentage ('25%'), a fraction ('1/4') or a number ('0.25')."
        ) from None

    return probability


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


def _draw(probability: float, num: int) -> list[bool]:
    """Draw num independent outcomes, each True with the given probability."""
    outcomes: list[bool] = []
    for _ in range(num):
        outcomes.append(random.random() < probability)

    return outcomes


class Probability:
    """
    The Probability class has useful functions that return True or False based on the given probability.

    Functions:

    - prob
    - iprob
    - set_constant
    - get
    - clear
    - count_values

    Note: All of them require creating an instance except the prob function

    Examples
    ----------

    Simple Usage:

    >>> from pyprobs import Probability as pr
    >>> pr.prob(50/100)  # You can pass float (i.e. 0.5, 0.157), int (i.e. 1, 0) or str (i.e. '50%', '3/11')
    False
    >>> pr.prob(50/100, num=5)
    [False, False, False, True, False]

    Suggested and More Advanced Usage:

    >>> from pyprobs import Probability as pr
    >>> p = pr()
    >>> p.iprob('3/7', 0.25, num=2)
    [[True, True], [False, False]]
    >>> p.history
    {'3/7': [True, True], 0.25: [False, False]}
    >>> p.count_values('all')
    {True: 2, False: 2}

    >>> p.set_constant(1/1000, mutable=True)  # If you set the mutable parameter to False, you won't be able to change the constant again.

    >>> p.get()  # You can get the constant and mutable value, also you can use it like "p.get(how='constant')" or "p.get(how='mutable')", this only returns the desired value.
    {'constant': 0.001, 'mutable': True}
    >>> p._constant # You can more easily get the constant value.
    0.001
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

        return _to_probability(self._constant)

    def __int__(self) -> int:
        return int(float(self))

    def __add__(self, other: object) -> "Probability":
        if not isinstance(other, Probability):
            return NotImplemented

        if self._constant == UNSET_CONSTANT or other._constant == UNSET_CONSTANT:
            raise exceptions.ConstantError("The objects' constants must be set before.")

        result = Probability()
        result.set_constant(min(float(self) + float(other), 1), self._mutable or other._mutable)
        return result

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Probability):
            return NotImplemented

        return self.get() == other.get()

    @staticmethod
    def prob(*args: ProbabilityValue, num: int = 1) -> bool | list[bool]:
        """
        General decision function that returns True or False based on the given probability.

        Args:
            *args: Probabilities given as int (1, 0), float (0.25, 1e-05) or str ('25%', '%12.5', '1/4', '0.25').
            num (int, optional): The number of how many times the function will run. Defaults to 1.

        Raises:
            NotGivenValueError: When no value was given
            NumError: When the num parameter was less than one
            ProbabilityTypeError: When the type of the given values are not among int, float, or str
            ProbabilityRangeError: When a given value is not between 0 and 1

        Returns:
            bool | list[bool]: If only one arg was given and num is 1, returns a bool value. Otherwise, returns a
            flat list that contains bool values.

        Examples:
            >>> from pyprobs import Probability as pr
            >>> pr.prob(1/2)
            True
            >>> pr.prob(0.778)
            False
            >>> pr.prob("25%")
            False
            >>> pr.prob("25%", num=5)
            [False, False, True, False, False]
        """
        if not args:
            raise exceptions.NotGivenValueError("No value was given.")

        num = _validate_num(num)

        probabilities: list[float] = []
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
        General decision function that returns True or False based on the given probability.

        This function can be only used when an instance was created from Probability. Every outcome is also stored in
        the instance's history, under the probability it was drawn for.

        Args:
            *args: Probabilities given as int (1, 0), float (0.25, 1e-05) or str ('25%', '%12.5', '1/4', '0.25'). If
                no args are given, the constant set with set_constant is used.
            num (int, optional): The number of how many times the function will run. Defaults to 1.

        Raises:
            NotGivenValueError: When no value was given and no constant was set
            NumError: When the num parameter was less than one and not int
            ProbabilityTypeError: When the type of the given values are not among int, float, or str
            ProbabilityRangeError: When a given value is not between 0 and 1

        Returns:
            bool | list[bool] | list[list[bool]]: If only one arg was given, returns a bool value when num is 1
            and a list of bool values otherwise. If more than one arg was given, returns one list per arg.

        Examples:
            >>> from pyprobs import Probability as pr
            >>> p = pr()
            >>> p.iprob(1/5)
            True
            >>> p.iprob(3/5, 0.15, num=2)
            [[True, True], [False, False]]

            You can set a constant and use iprob by not giving any args:

            >>> p.set_constant(0.5)  # You can also set a str constant, i.e "50%", "3/11".
            >>> p.iprob()
            True

            You can see the history:

            >>> p.history
            {0.2: [False], 0.6: [False, True], 0.15: [False, True], 0.5: [True]}

            You can count the values in the history:
            >>> p.count_values(which="all")  # the which parameter defaults to "last" and counts the last call's values
            {True: 1, False: 5}

        """
        if args:
            values = list(args)
        elif self._constant == UNSET_CONSTANT:
            raise exceptions.NotGivenValueError("No value was given and no constant was set.")
        else:
            values = [self._constant]

        num = _validate_num(num)

        probabilities: list[float] = []
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
        You can set an int, float, or str constant by calling this function.

        After setting a constant you don't need to pass any arguments to iprob. But if you pass any arguments to iprob,
        the arguments will be accepted not the constant. After setting the constant, you can get the constant by using
        the 'get' function.

        Args:
            constant (int | float | str): The constant value, can be int, float, or str
            mutable (bool, optional): If you set this False, you won't be allowed to change the instance's constant.
                Defaults to True.

        Raises:
            ConstantError: When the constant is not an int, float or str probability between 0 and 1.
            ImmutableConstantVariableError: If the mutable was set to False, when you call this function again, this
                error raises.

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
        Clears the instance's history.

        Basically does this:

        >>> <instance>.history.clear()
        """
        self.history.clear()

    def count_values(self, which: str = "last") -> dict[bool, int]:
        """
        Count the values in the instance's history.

        Args:
            which (str, optional): What values you want. 'last' counts the values returned by the last iprob call and
                'all' counts every value in the history. Defaults to 'last'.

        Raises:
            InvalidParameterValue: When the which parameter is not 'all' or 'last', this error raises.
            NotUsedError: Unless you use iprob function (and if the which parameter is set to 'last'), this error raises.

        Returns:
            dict[bool, int]: Returns a dict that contains the number of True values under the True key, and the number
            of False values under the False key.
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
        You can get the constant and/or mutable by calling this function.

        Args:
            how (str, optional): How you get the values. Can be 'constant&mutable', 'mutable&constant', 'constant' or
                'mutable'. Defaults to 'constant&mutable'.

        Raises:
            InvalidParameterValue: If the how parameter is not among 'constant&mutable', 'mutable&constant', 'constant'
                or 'mutable', this error raises.

        Returns:
            ConstantSettings | int | float | str | bool:
            - If you set the how parameter to 'constant&mutable', returns a dict with the 'constant' and 'mutable' keys.
            - If you set the how parameter to 'mutable&constant', returns the same dict with the 'mutable' key first.
            - If you set the how parameter to 'constant', returns only the constant value.
            - If you set the how parameter to 'mutable', returns only the mutable value.
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
