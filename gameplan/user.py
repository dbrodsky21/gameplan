import pandas as pd
import numpy as np
from typing import Callable, List, Optional, Union, Tuple
import shelve
import warnings
import zlib

from gameplan.assets import Asset
from gameplan.cashflows import CashFlow
from gameplan.collections import Collection, CashFlowCollection
from gameplan.expenses import Expenses
from gameplan.income_streams import IncomeStreams

class User():
    def __init__(self,
                 email: str,
                 birthday: Optional[pd.datetime] = None,
                 zip_code: Optional[int] = None,
                 gender: Optional[str] = None
                 ) -> None:
        self.email = email.lower()
        self.birthday = birthday
        self.zip_code = zip_code
        self.gender = gender

    @property
    def age(self):
        return pd.datetime.today() - self.age

    def get_income_percentile(self, source=None):
        pass
