# What is PyProbs?

PyProbs is a module that has useful functionality that returns True or False based on the given probability.

[![Version](https://img.shields.io/badge/Version-v0.3-orange)]()
[![Python](https://img.shields.io/badge/Python-v3.0%2B-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

## Installation

You can install it from [PyPI](https://pypi.org/project/pyprobs/) by running the following command

```
pip install pyprobs
```

Or you can manually execute the **setup.py** from [source](https://github.com/OmerFI/PyProbs)

```
python setup.py install
```

## Examples

Simple Usage:

```py
>>> from PyProbs import Probability as pr
>>> # You can pass float (i.e. 0.5, 0.157), int (i.e. 1, 0) or str (i.e. '50%', '3/11')
>>> pr.Prob(50/100)
False
>>> pr.Prob(50/100, num=5)
[False, False, False, True, False]
```

Suggested and More Advanced Usage:

```py
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
```

## Functions of The Probability Class

- Prob
- iProb
- set_constant
- get
- clear
- count_values

Note: All of them require creating an instance except the Prob function.

### Requirements

- Python _v3.x_

### Documentation

https://pyprobs.readthedocs.io/
