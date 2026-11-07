from importlib.metadata import version

from .probability import Probability

__version__ = version("pyprobs")

__all__ = ["Probability"]
