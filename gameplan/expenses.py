import pandas as pd
import numpy as np

from gameplan.cashflows import CashFlow
from gameplan.collections import CashFlowCollection


class Expense(CashFlow):
    def __init__(self, expense_type, amount=None, recurring=None, start_dt=None,
                 freq=None, end_dt=None, date_range=None, values=None, pretax=False,
                 growth_freq=pd.DateOffset(years=1), min_growth=0.0,
                 max_growth=0.0, growth_start_dt=None, growth_end_dt=None,
                 incorporate_growth=True, incorporate_discounting=True,
                 yearly_discount_rate=0.02, **kwargs):
        super().__init__(
            cashflow_type='expense',
            name=expense_type,
            amount=amount,
            start_dt=start_dt,
            end_dt=end_dt,
            freq=freq,
            recurring=recurring,
            date_range=date_range,
            values=values,
            outflow=True,
            growth_freq=growth_freq,
            min_growth=min_growth,
            max_growth=max_growth,
            growth_start_dt=growth_start_dt,
            growth_end_dt=growth_end_dt,
            incorporate_growth=incorporate_growth,
            incorporate_discounting=incorporate_discounting,
            yearly_discount_rate=yearly_discount_rate,
            **kwargs
        )
        self.pretax=pretax

    @property
    def _growth_fn(self):
        # Placeholder; will want better logic around distributions
        grwth = lambda x: 1 + np.random.uniform(low=self.min_growth,
                                                high=self.max_growth)
        return grwth


    def get_growth_path(self, return_df=False, start_dt=None, end_dt=None,
                        growth_freq=None, growth_fn=None):
        return super().get_growth_path(
            return_df=return_df,
            start_dt=start_dt if start_dt else self.growth_start_dt,
            end_dt=end_dt if end_dt else self.growth_end_dt,
            growth_freq=growth_freq if growth_freq else self.growth_freq,
            growth_fn=growth_fn if growth_fn else self._growth_fn
        )

    def update_values_with_growth(self, start_dt=None, end_dt=None,
                                  growth_freq=None, growth_fn=None):
        super().update_values_with_growth(
            start_dt=start_dt if start_dt else self.growth_start_dt,
            end_dt=end_dt if end_dt else self.growth_end_dt,
            growth_freq=growth_freq if growth_freq else self.growth_freq,
            growth_fn=growth_fn if growth_fn else self._growth_fn
        )

class Rent(Expense):
    def __init__(self, amount, start_dt=pd.datetime.today(), freq='MS',
                 end_dt=pd.datetime.today() + pd.DateOffset(years=20),
                 growth_freq=pd.DateOffset(years=1), min_growth=0.0,
                 max_growth=0.0, growth_start_dt=None, growth_end_dt=None,
                 **kwargs):
        super().__init__(
            expense_type='rent',
            amount=amount,
            recurring=True,
            start_dt=start_dt,
            freq=freq,
            end_dt=end_dt,
            growth_freq=growth_freq,
            min_growth=min_growth,
            max_growth=max_growth,
            growth_start_dt=growth_start_dt,
            growth_end_dt=growth_end_dt,
            **kwargs
        )


class Utilities(Expense):
    def __init__(self, amount, start_dt=pd.datetime.today(), freq='MS',
                 end_dt=pd.datetime.today() + pd.DateOffset(years=20),
                 growth_freq=pd.DateOffset(years=1), min_growth=0.0,
                 max_growth=0.0, growth_start_dt=None, growth_end_dt=None,
                 **kwargs):
        super().__init__(
            expense_type='utilities',
            amount=amount,
            recurring=True,
            start_dt=start_dt,
            freq=freq,
            end_dt=end_dt,
            growth_freq=growth_freq,
            min_growth=min_growth,
            max_growth=max_growth,
            growth_start_dt=growth_start_dt,
            growth_end_dt=growth_end_dt,
            **kwargs
        )


class Expenses(CashFlowCollection):
    def __init__(self, expenses={}):
        super().__init__(collection_type=Expense, objects=expenses)

    @property
    def pretax(self):
        return {k: v for k,v in self.contents.items() if v.pretax}

    @property
    def post_tax(self):
        return {k: v for k,v in self.contents.items() if not v.pretax}
