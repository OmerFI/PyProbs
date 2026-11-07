Examples
========

Draw without setup
------------------

.. code-block:: pycon

    >>> from pyprobs import Probability as pr
    >>> pr.prob(0.5)
    True
    >>> pr.prob("25%", num=5)
    [False, False, True, False, False]
    >>> pr.prob(1, 0)  # Several probabilities return one flat list
    [True, False]

Keep a history
--------------

.. code-block:: pycon

    >>> p = pr()
    >>> p.iprob("3/7", 0.25, num=2)
    [[True, True], [False, False]]
    >>> p.history
    {'3/7': [True, True], 0.25: [False, False]}
    >>> p.count_values("all")
    {True: 2, False: 2}

Set a constant
--------------

When most of your calls use the same probability, set it once and call ``iprob()`` without arguments. Passing
``mutable=False`` locks it, so a later ``set_constant()`` raises an error.

.. code-block:: pycon

    >>> p.set_constant("1/1000", mutable=False)
    >>> p.iprob()
    False
    >>> p.get()
    {'constant': '1/1000', 'mutable': False}

Supported notations
-------------------

.. list-table::
   :header-rows: 1

   * - Form
     - Examples
   * - int
     - ``0``, ``1``
   * - float
     - ``0.25``, ``1e-05``
   * - Percentage
     - ``"25%"``, ``"%12.5"``
   * - Fraction
     - ``"1/4"``, ``" 3 / 7 "``
   * - Number
     - ``"0.25"``

A value outside the 0–1 range raises ``ProbabilityRangeError``, and a str that cannot be read as a probability raises
``ProbabilityTypeError``.
