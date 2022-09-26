from random import randint as _randint
from . import exceptions
from typing import Union, Iterable, Dict


class Probability(object):
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
        self._constant = "unset"
        self._args = False
        self.history = {}

    def __str__(self) -> str:
        return str(
            f"Probability(_constant='{self._constant}', _mutable={self._mutable})"
        )

    def __float__(self) -> float:
        return float(self._constant)

    def __int__(self) -> int:
        return int(self._constant)

    def __add__(self, other):
        if not isinstance(other, Probability):
            return NotImplemented
        if self._constant == "unset" or other._constant == "unset":
            raise exceptions.ConstantError("The objects' constants must be set before.")
        result = __class__()
        result_constant = self._constant + other._constant
        result_mutable = self._mutable | other._mutable
        if result_constant > 1.0:
            result_constant = 1
        result.set_constant(result_constant, result_mutable)
        return result

    def __eq__(self, other) -> bool:
        if self.get() == other.get():
            return True
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    @staticmethod
    def _int_probability(arg: int) -> bool:
        if arg == 1:
            return True
        elif arg == 0:
            return False
        else:
            raise exceptions.ProbabilityRangeError(
                "The probability of an event must be between 0 and 1."
            )

    @classmethod
    def _float_probability(cls, arg: float) -> bool:
        if arg % 1 == 0:
            if cls._int_probability(arg):
                return True
            return False
        elif arg > 1 or arg < 0:
            raise exceptions.ProbabilityRangeError(
                "The probability of an event must be between 0 and 1."
            )

        second_part = str(arg).split(".")[1]
        value = _randint(1, 10 ** len(second_part))
        if int(second_part) >= value:
            return True
        return False

    @classmethod
    def _str_probability(cls, arg: str) -> bool:
        if "%" in arg and "/" in arg:
            return NotImplemented  # can change later

        if "%" in arg:
            arg = (
                arg.split("%")[1].strip()
                if arg[0] == "%"
                else arg.split("%")[0].strip()
            )
            return cls._float_probability(int(arg.strip()) / 100)
        elif "/" in arg:
            arg = arg.split("/")
            first_part = int(arg[0])
            second_part = int(arg[1])
            value = _randint(1, second_part)
            if first_part >= value:
                return True
            return False

    @staticmethod
    def _adjust_str(arg: str) -> str:
        if "/" in arg:
            arg_as_list = arg.strip().split("/")
            for idx, t in enumerate(arg_as_list):
                arg_as_list[idx] = t.strip()
            return "/".join(arg_as_list)
        elif "%" in arg:
            arg_as_list = arg.strip().split("%")
            for idx, t in enumerate(arg_as_list):
                arg_as_list[idx] = t.strip()
            return "%".join(arg_as_list)

    @classmethod
    def prob(cls, *args, num: int = 1) -> Union[bool, Iterable[bool]]:
        """
        General decision function that returns True or False based on the given probability.

        Args:
            num (int, optional): The number of how many times the function will run. Defaults to 1.

        Raises:
            NotGivenValueError: When no value was given
            NumError: When the num parameter was less than one
            ProbabilityTypeError: When the type of the given values are not among int, float, or str

        Returns:
            Union[bool, Iterable[bool]]: If only one arg was given, returns a bool value. Otherwise, returns a list that contains bool values.

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
        values = []

        if not args:
            raise exceptions.NotGivenValueError("No value was given.")

        if num < 1:
            raise exceptions.NumError("The num parameter must be at least one.")

        for arg in args:
            if isinstance(arg, int):
                for _ in range(num):
                    if cls._int_probability(arg):
                        values.append(True)
                    else:
                        values.append(False)
            elif isinstance(arg, float):
                for _ in range(num):
                    if cls._float_probability(arg):
                        values.append(True)
                    else:
                        values.append(False)
            elif isinstance(arg, str):
                for _ in range(num):
                    if cls._str_probability(arg):
                        values.append(True)
                    else:
                        values.append(False)
            else:
                raise exceptions.ProbabilityTypeError(
                    "The type which you gave to prob must be int, float, or str."
                )

        if len(values) > 1:
            return values
        else:
            return values[0]

    def iprob(self, *args, num: int = 1) -> Union[bool, Iterable[bool]]:
        """
        General decision function that returns True or False based on the given probability.
        This function can be only used when an instance was created from Probability.

        Args:
            num (int, optional): The number of how many times the function will run. Defaults to 1.

        Raises:
            NotGivenValueError: When no value was given
            NumError: When the num parameter was less than one and not int
            ProbabilityTypeError: When the type of the given values are not among int, float, or str

        Returns:
            Union[bool, Iterable[bool]]: If only one arg was given, returns a bool value. Otherwise, returns a list that contains bool values.

        Examples:
            >>> from pyprobs import Probability as pr
            >>> p = pr()
            >>> p.iprob(1/5)
            True
            >>> p.iprob(3/5, 0.15, num=2)
            [[True, True], [False, False]]

            You can set a constant and use iprob by not giving any args:

            >>> p.set_constant(0.5)  # You can also set a str constant, i.e "50%", "3/11". For more accurate results, give them as str.
            >>> p.iprob()
            True

            You can see the history:

            >>> p.history
            {0.2: [False], 0.6: [False, True], 0.15: [False, True], 0.5: [True]}

            You can count the values in the history:
            >>> p.count_values(which="all")  # the which parameter defaults to "last" and returns the last value in the history
            {True: 1, False: 5}

        """
        _values = []
        self._last_values = []
        args = list(args)  # converting tuple to list
        if not args:
            if self._constant == "unset":
                raise exceptions.NotGivenValueError(
                    "No value was given and no constant was set."
                )
            args = [self._constant]
            self._args = False
        else:
            self._args = True

        if isinstance(num, float):
            if num % 1 == 0:
                num = int(num)
            else:
                raise exceptions.NumError(
                    "The num parameter must be int and at least one"
                )

        if num < 1:
            raise exceptions.NumError("The num parameter must be at least one.")

        for idx, arg in enumerate(args):
            if isinstance(arg, int):
                for _ in range(num):
                    if self._int_probability(arg):
                        _values.append(True)
                    else:
                        _values.append(False)
            elif isinstance(arg, float):
                for _ in range(num):
                    if self._float_probability(arg):
                        _values.append(True)
                    else:
                        _values.append(False)
            elif isinstance(arg, str):
                arg = self._adjust_str(arg)
                args[idx] = arg
                for _ in range(num):
                    if self._str_probability(arg):
                        _values.append(True)
                    else:
                        _values.append(False)
            else:
                raise exceptions.ProbabilityTypeError(
                    "The type which you gave to iprob must be int, float, or str."
                )

            # constant was set, args were given.
            if self._constant != "unset" and self._args:
                if arg not in self.history.keys():
                    self.history.update({arg: _values})
                else:
                    for value in _values:
                        self.history[arg].append(value)
            # constant was set, args were not given.
            elif self._constant != "unset" and not self._args:
                if arg in self.history.keys():
                    for x in _values:
                        self.history[arg].append(x)
                else:
                    self.history.update({arg: _values})
                # constant was unset, args were given.
            elif self._constant == "unset" and self._args:
                if arg not in self.history.keys():
                    self.history.update({arg: _values})
                else:
                    for value in _values:
                        self.history[arg].append(value)
            _values = []

        __values = []
        LASTADDED = slice(-num, None)
        for arg in args:
            __values.append(self.history[arg][LASTADDED])
        if len(__values) == 1:
            if len(__values[0]) == 1:
                self._last_values.append(__values[0][0])
                return __values[0][0]
            self._last_values.append(__values[0])
            return __values[0]
        else:
            self._last_values.append(__values)
            return __values

    def set_constant(
        self, constant: Union[int, float, str], mutable: bool = True
    ) -> None:
        """
        You can set an int, float, or str constant by calling this function. After setting a constant you don't need to pass any arguments to iprob.
        But if you pass any arguments to iprob, the arguments will be accepted not the constant.
        After setting the constant, you can get the constant by using the 'get' function.

        Args:
            constant (Union[int, float, str]): The constant value, can be int, float, or str
            mutable (bool, optional): If you set this False, you won't be allowed to change the instance's constant. Defaults to True.

        Raises:
            ConstantError: The constant parameter must be int, float, or str.
            ImmutableConstantVariableError: If the mutable was set to False, when you call this function again, this error raises.

        """
        if not isinstance(constant, (int, float, str)):
            raise exceptions.ConstantError(
                "The constant parameter must be int, float or str."
            )
        else:
            if isinstance(constant, (int, float)):
                if float(constant) < 0 or float(constant) > 1:
                    raise exceptions.ConstantError(
                        "The constant parameter must be between 0 and 1."
                    )
            else:
                if ("%" not in constant) and ("/" not in constant):
                    raise exceptions.ConstantError(
                        "If the constant parameter was set to str, it must contain '%' or '/'."
                    )

        if self._mutable:
            self._constant = constant
            if not mutable:
                self._mutable = False
        else:
            raise exceptions.ImmutableConstantVariableError(
                "The mutable parameter has been set False before. You cannot set a constant again."
            )

    def clear(self) -> None:
        """
        Clears the instance's history.

        Basically does this:

        >>> <instance>.history.clear()
        """
        self.history.clear()

    def count_values(self, which: str = "last") -> Dict[bool, int]:
        """
        Count the values in the instance's history

        Args:
            which (str, optional): What values you want. Can be 'last' or 'all'. Defaults to 'last'.

        Raises:
            InvalidParameterValue: When the which parameter is not 'all' or 'last', this error raises.
            NotUsedError: Unless you use iprob function (and if the which parameter is set to 'last'), this error raises.

        Returns:
            Dict[bool, int]: Returns a dict that contains True values in the key, and False values in the value.
        """
        if which not in ["all", "last"]:
            raise exceptions.InvalidParameterValue(
                "The which parameter can be only 'all' or 'last'."
            )
        _true_counter = 0
        _false_counter = 0
        if which == "all":
            for list_ in self.history.values():
                for value in list_:
                    if value:
                        _true_counter += 1
                    else:
                        _false_counter += 1
        elif which == "last":
            try:
                if len(self._last_values) == 1 and not isinstance(
                    self._last_values[0], list
                ):
                    if self._last_values[0]:
                        _true_counter += 1
                    else:
                        _false_counter += 1
                else:
                    for value in self._last_values[0]:
                        if value:
                            _true_counter += 1
                        else:
                            _false_counter += 1
            except AttributeError:
                raise exceptions.NotUsedError(
                    "iprob function must be used at least 1 time before."
                )

        return {True: _true_counter, False: _false_counter}

    def get(
        self, how: str = "constant&mutable"
    ) -> Union[Dict[str, Union[int, float, bool, str]], int, float, bool, str]:
        """
        You can get the constant and/or mutable by calling this function.

        Args:
            how (str, optional): How you get the values. Can be 'constant&mutable', 'mutable&constant', 'constant' or 'mutable'. Defaults to 'constant&mutable'.

        Raises:
            InvalidParameterValue: If the how parameter is not among 'constant&mutable', 'mutable&constant', 'constant' or 'mutable', this error raises.

        Returns:
            Union[Dict[str, Union[int, float, bool, str]], int, float, bool, str]:
            - If you set the how parameter to 'constant&mutable', returns a dict that contains the constant in the key and mutable in the value.
            - If you set the how parameter to 'mutable&constant', returns a dict that contains the mutable in the key and constant in the value.
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
