#from . import interfaces  # noqa
from . import gather  # noqa
from . import datasets

from .gather import (gather_conmats, gather_results)
from .datasets import fetch_omega_dataset, fetch_ieeg_dataset

__version__ = '0.3.dev0'
