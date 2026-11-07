import random
from typing import Any

import pytest

from pyprobs import Probability as pr
from pyprobs import exceptions
from pyprobs.probability import ProbabilityValue


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ((1 / 2), [True, False]),
        (0.778, [True, False]),
        (1e-05, [True, False]),
        ("3/4", [True, False]),
        (" 3 / 4 ", [True, False]),
        ("0.48", [True, False]),
        ("25%", [True, False]),
        ("12.5%", [True, False]),
        ("%69", [True, False]),
        ("% 69", [True, False]),
    ],
)
def test_prob_in(test_input: ProbabilityValue, expected: list[bool]) -> None:
    assert pr.prob(test_input) in expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (0.0, False),
        (0, False),
        (1.0, True),
        (1, True),
        ("0%", False),
        ("100%", True),
        ("0/7", False),
        ("7/7", True),
        ("0.0", False),
        ("1", True),
    ],
)
def test_prob_equals(test_input: ProbabilityValue, expected: bool) -> None:
    assert pr.prob(test_input) == expected


@pytest.mark.parametrize(
    "test_input,num,expected",
    [
        ("3/4", 2, 2),
        ("0.48", 3, 3),
        ("25%", 4, 4),
        ("%69", 5, 5),
    ],
)
def test_prob_len(test_input: ProbabilityValue, num: int, expected: int) -> None:
    values = pr.prob(test_input, num=num)

    assert isinstance(values, list)
    assert len(values) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (0.3, 0.3),
        ("30%", 0.3),
        ("3/10", 0.3),
        ("0.3", 0.3),
        (1e-05, 0),
    ],
)
def test_prob_frequency(test_input: ProbabilityValue, expected: float) -> None:
    random.seed(0)
    values = pr.prob(test_input, num=10_000)

    assert isinstance(values, list)
    assert sum(values) / len(values) == pytest.approx(expected, abs=0.02)


def test_prob_multiple_args_returns_flat_list() -> None:
    assert pr.prob(1, 0, num=2) == [True, True, False, False]


@pytest.mark.parametrize("test_input", [2, -1, 1.5, "3/2", "150%", "-0.1"])
def test_prob_out_of_range(test_input: ProbabilityValue) -> None:
    with pytest.raises(exceptions.ProbabilityRangeError):
        pr.prob(test_input)


@pytest.mark.parametrize("test_input", [None, [0.5], "abc", "50%/2", "1/0", "1/2/3"])
def test_prob_invalid_value(test_input: Any) -> None:
    with pytest.raises(exceptions.ProbabilityTypeError):
        pr.prob(test_input)


def test_no_value_given() -> None:
    with pytest.raises(exceptions.NotGivenValueError):
        pr.prob()

    with pytest.raises(exceptions.NotGivenValueError):
        pr().iprob()


@pytest.mark.parametrize("num", [0, -1, 1.5])
def test_invalid_num(num: Any) -> None:
    with pytest.raises(exceptions.NumError):
        pr.prob(0.5, num=num)

    with pytest.raises(exceptions.NumError):
        pr().iprob(0.5, num=num)


def test_integral_float_num() -> None:
    num: Any = 2.0

    assert pr.prob(1, num=num) == [True, True]
    assert pr().iprob(1, num=num) == [True, True]


def test_iprob_return_shapes() -> None:
    p = pr()

    assert p.iprob(1) is True
    assert p.iprob(0, num=2) == [False, False]
    assert p.iprob(1, 0) == [[True], [False]]
    assert p.iprob(1, 0, num=2) == [[True, True], [False, False]]


def test_iprob_history() -> None:
    p = pr()
    p.iprob(" 1 / 1 ", 0, num=2)
    p.iprob(0)

    assert p.history == {"1/1": [True, True], 0: [False, False, False]}


def test_iprob_same_arg_twice_returns_each_draw() -> None:
    p = pr()
    values = p.iprob(0.5, 0.5, num=3)

    assert values == [p.history[0.5][:3], p.history[0.5][3:]]


def test_iprob_numeric_str() -> None:
    p = pr()

    assert p.iprob("1.0") is True
    assert p.history == {"1.0": [True]}


def test_iprob_uses_constant() -> None:
    p = pr()
    p.set_constant("100%")

    assert p.iprob() is True
    assert p.iprob(0) is False
    assert p.history == {"100%": [True], 0: [False]}


def test_count_values_last_with_multiple_args() -> None:
    p = pr()

    p.iprob(0, 0, num=2)
    assert p.count_values() == {True: 0, False: 4}

    p.iprob(1, 0)
    assert p.count_values() == {True: 1, False: 1}
    assert p.count_values("all") == {True: 1, False: 5}


def test_count_values_errors() -> None:
    p = pr()

    with pytest.raises(exceptions.NotUsedError):
        p.count_values()

    assert p.count_values("all") == {True: 0, False: 0}

    with pytest.raises(exceptions.InvalidParameterValue):
        p.count_values("first")


def test_clear() -> None:
    p = pr()
    p.iprob(1)
    p.clear()

    assert p.history == {}


def test_set_constant_and_get() -> None:
    p = pr()
    assert p.get() == {"constant": "unset", "mutable": True}

    p.set_constant("3/7", mutable=False)
    assert p.get() == {"constant": "3/7", "mutable": False}
    assert p.get("mutable&constant") == {"mutable": False, "constant": "3/7"}
    assert p.get("constant") == "3/7"
    assert p.get("mutable") is False

    with pytest.raises(exceptions.ImmutableConstantVariableError):
        p.set_constant(0.5)

    with pytest.raises(exceptions.InvalidParameterValue):
        p.get("other")


@pytest.mark.parametrize("constant", [None, 1.5, "abc", "150%", "3/2"])
def test_set_constant_invalid(constant: Any) -> None:
    with pytest.raises(exceptions.ConstantError):
        pr().set_constant(constant)


def test_dunder_methods() -> None:
    p = pr()
    p.set_constant("50%")
    q = pr()
    q.set_constant(0.25, mutable=False)

    assert str(p) == "Probability(_constant='50%', _mutable=True)"
    assert float(p) == 0.5
    assert int(p) == 0
    assert (p + q).get() == {"constant": 0.75, "mutable": True}
    assert (p + p + p).get("constant") == 1
    assert p != q
    assert p != "50%"

    same = pr()
    same.set_constant("50%")
    assert p == same


def test_add_errors() -> None:
    with pytest.raises(exceptions.ConstantError):
        _ = pr() + pr()

    with pytest.raises(TypeError):
        _ = pr() + 1
