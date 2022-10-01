from pyprobs import *

from setuptools.config.setupcfg import read_configuration

config = read_configuration("setup.cfg")
doc_link = config["metadata"]["project_urls"]["Documentation"]

deprecation_message = f"""\
Importing from "PyProbs" is deprecated and will be removed in a future
version. Please import from "pyprobs" instead. For example:
    >>> from pyprobs import Probability as pr

Also some of the functions listed below have been renamed:
- Prob -> prob
- iProb -> iprob

See the documentation for more details:
{doc_link}
"""

print(deprecation_message)
