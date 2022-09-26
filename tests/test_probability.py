import pytest
from pyprobs import Probability as pr


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ((1 / 2), [True, False]),
        (0.778, [True, False]),
        ("3/4", [True, False]),
        ("0.48", [True, False]),
        ("25%", [True, False]),
        ("%69", [True, False]),
    ],
)
def test_prob_in(test_input, expected):
    assert pr.prob(test_input) in expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (0.0, False),
        (0, False),
        (1.0, True),
        (1, True),
    ],
)
def test_prob_equals(test_input, expected):
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
def test_prob_len(test_input, num, expected):
    assert len(pr.prob(test_input, num=num)) == expected


# TODO: Add more tests for prob() and iprob()
