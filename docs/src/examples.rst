Examples
========

Simple usage:

.. code-block:: python

    >>> from pyprobs import Probability as pr
    >>> # You can pass float (i.e. 0.5, 0.157), int (i.e. 1, 0) or str (i.e. '50%', '3/11')
    >>> pr.prob(50/100)
    False
    >>> pr.prob(50/100, num=5)
    [False, False, False, True, False]

Suggested and more advanced usage:

.. code-block:: python

    >>> from PyProbs import Probability as pr
    >>> p = pr()
    >>> p.iProb('3/7', 0.25, num=2)
    [[True, True], [False, False]]

    >>> p.history
    {'3/7': [True, True], 0.25: [False, False]}
    >>> p.count_values('all')
    {True: 2, False: 2}

    >>> p.set_constant(1/1000, mutable=True)  # If you set the mutable parameter to False, you won't be able to change the constant again.

    >>> # You can get the constant and mutable value:
    >>> p.get()
    {'constant': 0.001, 'mutable': True}
    >>> # Also you can use it like "p.get(how='constant')" or "p.get(how='mutable')", this only returns the desired value.

    >>> p._constant # You can more easily get the constant value.
    0.001
