from datetime import datetime
import pandas as pd
import numpy as np
from typing import Callable, List, Optional, Union, Tuple

from gameplan.cashflows import CashFlow
from gameplan.collections import CashFlowCollection
from gameplan.growth.growth_series import GrowthSeries, LinearGrowth, LogisticGrowth, StochasticGrowth

class Expense(CashFlow):
    def __init__(self,
                 expense_type: str,
                 date_range: pd.date_range = None,
                 amount: Optional[float] = None,
                 values: Optional[List[float]] = None,
                 recurring: Optional[bool] = None,
                 freq: Optional[str] = None,
                 start_dt: Optional[Union[str, datetime]] = None,
                 end_dt: Optional[Union[str, datetime]] = None,
                 growth_series: GrowthSeries = GrowthSeries,
                 growth_freq: pd.DateOffset = pd.DateOffset(years=1),
                 min_growth: Optional[float] = None,
                 max_growth: Optional[float] = None,
                 growth_start_dt: Optional[Union[str, datetime]] = None,
                 growth_end_dt: Optional[Union[str, datetime]] = None,
                 growth_per_period_fn: Optional[Callable] = None,
                 incorporate_growth: bool = True,
                 incorporate_discounting: bool = True,
                 yearly_discount_rate: float = 0.02,
                 local_vol: float = 0.0,
                 pretax=False,
                 **kwargs
                 ) -> None:
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
    def __init__(self,
                 amount: float,
                 start_dt: datetime = pd.datetime.today(),
                 end_dt: datetime = pd.datetime.today() + pd.DateOffset(years=20),
                 freq: Union[str, datetime] = 'MS',
                 growth_series: GrowthSeries = LogisticGrowth,
                 growth_points_to_fit: List[Tuple[int, float]] = [(0,1), (5*365, 1.75), (10*365, 2.25)],
                 growth_per_period_fn: Optional[Callable] = None,
                 growth_freq: Union[str, datetime] = pd.DateOffset(years=1),
                 min_growth: Optional[float] = None,
                 max_growth: Optional[float] = None,
                 growth_start_dt: Optional[Union[str, datetime]] = None,
                 growth_end_dt: Optional[Union[str, datetime]] = None,
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
    def __init__(self,
                 amount: float,
                 start_dt: datetime = pd.datetime.today(),
                 end_dt: datetime = pd.datetime.today() + pd.DateOffset(years=20),
                 freq: Union[str, datetime] = 'MS',
                 growth_series: GrowthSeries = LinearGrowth,
                 growth_points_to_fit: List[Tuple[int, float]] = [(0,1), (365, 1.02)],
                 growth_freq: Union[str, datetime] = pd.DateOffset(years=1),
                 min_growth: Optional[float] = None,
                 max_growth: Optional[float] = None,
                 growth_start_dt: Optional[Union[str, datetime]] = None,
                 growth_end_dt: Optional[Union[str, datetime]] = None,
                 local_vol: float = 0.15,
                 **kwargs
                 ) -> None:
        super().__init__(
            expense_type='utilities',
            amount=amount,
            recurring=True,
            start_dt=start_dt,
            freq=freq,
            end_dt=end_dt,
            growth_series = growth_series,
            growth_freq=growth_freq,
            min_growth=min_growth,
            max_growth=max_growth,
            growth_start_dt=growth_start_dt,
            growth_end_dt=growth_end_dt,
            addtl_growth_params=dict(points_to_fit=growth_points_to_fit),
            local_vol=local_vol,
            **kwargs
        )


class MiscellaneousExpenses(Expense):
    def __init__(self,
                 amount: float,
                 start_dt: datetime = pd.datetime.today(),
                 end_dt: datetime = pd.datetime.today() + pd.DateOffset(years=20),
                 freq: Union[str, datetime] = 'MS',
                 growth_series: GrowthSeries = LogisticGrowth,
                 growth_points_to_fit: List[Tuple[int, float]] = [(0,1), (5*365, 1.25), (10*365, 1.4)],
                 growth_freq: Union[str, datetime] = pd.DateOffset(months=1),
                 min_growth: Optional[float] = None,
                 max_growth: Optional[float] = None,
                 growth_start_dt: Optional[Union[str, datetime]] = None,
                 growth_end_dt: Optional[Union[str, datetime]] = None,
                 local_vol: float = 0.15,
                 **kwargs
                 ) -> None:
        super().__init__(
            expense_type='misc_spending',
            amount=amount,
            recurring=True,
            start_dt=start_dt,
            freq=freq,
            end_dt=end_dt,
            growth_series = growth_series,
            growth_freq=growth_freq,
            min_growth=min_growth,
            max_growth=max_growth,
            growth_start_dt=growth_start_dt,
            growth_end_dt=growth_end_dt,
            addtl_growth_params=dict(points_to_fit=growth_points_to_fit),
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
