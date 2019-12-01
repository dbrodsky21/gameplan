import pandas as pd
import numpy as np
from typing import Callable, List, Optional, Union, Tuple

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

    def get_growth_curve(self, object_type, model):
        pass
