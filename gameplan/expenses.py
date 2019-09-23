import pandas as pd
import numpy as np

from gameplan.cashflows import CashFlow
from gameplan.collections import CashFlowCollection
from gameplan.growth_series import GrowthSeries, LogisticGrowth, StochasticGrowth

class Expense(CashFlow):
    def __init__(self, expense_type, amount=None, recurring=None, start_dt=None,
                 freq=None, end_dt=None, date_range=None, values=None, pretax=False,
                 growth_series=GrowthSeries, growth_per_period_fn=None,
                 growth_freq=pd.DateOffset(years=1), min_growth=None,
                 max_growth=None, growth_start_dt=None, growth_end_dt=None,
                 incorporate_growth=True, incorporate_discounting=True,
                 yearly_discount_rate=0.02, local_vol=0.0, **kwargs):
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
            growth_series = growth_series,
            growth_per_period_fn=growth_per_period_fn,
            growth_freq=growth_freq,
            min_growth=min_growth,
            max_growth=max_growth,
            growth_start_dt=growth_start_dt,
            growth_end_dt=growth_end_dt,
            incorporate_growth=incorporate_growth,
            incorporate_discounting=incorporate_discounting,
            yearly_discount_rate=yearly_discount_rate,
            local_vol=local_vol,
            **kwargs
        )
        self.pretax=pretax


    @property
    def _local_vol_fn(self):
        # Normal dist w/ std as % of mean value, based on self._local_vol
        return lambda x: np.random.normal(x, scale=x*self._local_vol)


class Rent(Expense):
    def __init__(self, amount, start_dt=pd.datetime.today(), freq='MS',
                 end_dt=pd.datetime.today() + pd.DateOffset(years=20),
                 growth_series=LogisticGrowth,
                 growth_points_to_fit=[(0,1), (5*365, 1.75), (10*365, 2.25)],
                 growth_per_period_fn=None,
                 growth_freq=pd.DateOffset(years=1), min_growth=None,
                 max_growth=None, growth_start_dt=None, growth_end_dt=None,
                 **kwargs):
        super().__init__(
            expense_type='rent',
            amount=amount,
            recurring=True,
            start_dt=start_dt,
            freq=freq,
            end_dt=end_dt,
            growth_series = growth_series,
            growth_per_period_fn=growth_per_period_fn,
            growth_freq=growth_freq,
            min_growth=min_growth,
            max_growth=max_growth,
            growth_start_dt=growth_start_dt,
            growth_end_dt=growth_end_dt,
            addtl_growth_params=dict(points_to_fit=growth_points_to_fit),
            local_vol=0.0,
            **kwargs
        )


class Utilities(Expense):
    def __init__(self, amount, start_dt=pd.datetime.today(), freq='MS',
                 end_dt=pd.datetime.today() + pd.DateOffset(years=20),
                 growth_series=StochasticGrowth,
                 growth_per_period_fn=lambda x: .0,
                 growth_freq=pd.DateOffset(years=1), min_growth=None,
                 max_growth=None, growth_start_dt=None, growth_end_dt=None,
                 local_vol=0.15, **kwargs):
        super().__init__(
            expense_type='utilities',
            amount=amount,
            recurring=True,
            start_dt=start_dt,
            freq=freq,
            end_dt=end_dt,
            growth_series = growth_series,
            growth_per_period_fn=growth_per_period_fn,
            growth_freq=growth_freq,
            min_growth=min_growth,
            max_growth=max_growth,
            growth_start_dt=growth_start_dt,
            growth_end_dt=growth_end_dt,
            local_vol=local_vol,
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
