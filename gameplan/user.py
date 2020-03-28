import pandas as pd
import numpy as np
from typing import Callable, List, Optional, Union, Tuple

from gameplan.growth.growth_models import KitcesIncomeGrowthModel

class User():
    def __init__(self,
                 email: str,
                 birthday: Optional[pd.datetime] = None,
                 zip_code: Optional[int] = None,
                 gender: Optional[str] = None,
                 income_percentile: int = 50
                 ) -> None:
        self.email = email.lower()
        self.birthday = birthday
        self.zip_code = zip_code
        self.gender = gender
        self._income_percentile = income_percentile

    @property
    def age(self) -> pd.Timedelta:
        return pd.datetime.today() - self.birthday

    @property
    def income_percentile(self) -> int:
        return self._income_percentile

    @income_percentile.setter
    def income_percentile(self, val: int) -> None:
        # TO DO: implement a get_income_percentile method to estimate
        # this based on user demographic and other info
        self._income_percentile = val

    def get_growth_points_to_fit(self,
                                 growth_model: KitcesIncomeGrowthModel,
                                 start_dt: pd.datetime = pd.datetime.today(),
                                 **kwargs
                                 ) -> pd.Series:
        gm = growth_model(user_birthday=self.birthday,
                          income_percentile=self.income_percentile)
        return gm.get_growth_points_to_fit(start_dt=start_dt)
