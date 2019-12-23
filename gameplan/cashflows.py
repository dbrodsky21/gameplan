from datetime import datetime
import numpy as np
import pandas as pd
from typing import Callable, List, Optional, Union
import warnings

from gameplan.growth.growth_series import GrowthSeries
import gameplan.helpers as hp


class CashFlow():
    DEFAULT_END_DT_OFFSET = pd.DateOffset(years=20)

    def __init__(self,
                 cashflow_type: str,
                 name: str,
                 date_range: pd.date_range = None,
                 values: Optional[List[float]] = None,
                 amount: Optional[float] = None,
                 recurring: Optional[bool] = None,
                 freq: Optional[str] = None,
                 start_dt: Optional[Union[str, datetime]] = None,
                 end_dt: Optional[Union[str, datetime]] = None,
                 outflow: bool = False,
                 growth_series: GrowthSeries = GrowthSeries,
                 growth_freq: pd.DateOffset = pd.DateOffset(years=1),
                 min_growth: Optional[float] = None,
                 max_growth: Optional[float] = None,
                 growth_start_dt: Optional[Union[str, datetime]] = None,
                 growth_end_dt: Optional[Union[str, datetime]] = None,
                 growth_per_period_fn: Optional[Callable] = None,
                 addtl_growth_params: dict = {},
                 incorporate_growth: bool = False,
                 incorporate_discounting: bool = False,
                 yearly_discount_rate: float = 0.02,
                 local_vol: float = 0.0,
                 **kwargs
                 ) -> None:
        """
        """
        self._cashflow_type = cashflow_type
        self.name = name
        start_dt = pd.Timestamp(start_dt) if start_dt else None
        end_dt = pd.Timestamp(end_dt) if end_dt else None
        if date_range is not None:
            self.start_dt = date_range.min()
            self.end_dt = date_range.max()
            self.freq = date_range.freq
        else:
            self.start_dt = start_dt
            self.end_dt = start_dt if not recurring else (
                end_dt if end_dt
                else start_dt + self.DEFAULT_END_DT_OFFSET
            )
            self.freq=freq

        self.amount = amount
        self._initial_values = values if values is not None else (
            [amount] * len(self.date_range)
        )
        self._values = self._initial_values # We may want to change values, e.g. growth in salary/expenses, but want to still have a record of original _values
        self._outflow = outflow
        self.growth_series = growth_series(
            start_dt=growth_start_dt or self.date_range.min(),
            end_dt=growth_end_dt or self.date_range.max(),
            freq=growth_freq or self.freq,
            min_val=min_growth,
            max_val=max_growth,
            growth_per_period_fn=growth_per_period_fn or (lambda x: 0),
            **addtl_growth_params
        )
        self._yearly_discount_rate = yearly_discount_rate
        self._incorporate_growth = incorporate_growth
        self._incorporate_discounting = incorporate_discounting
        self._local_vol = local_vol
        if incorporate_growth:
            self.update_values_with_growth() # will update discounting as well
        elif incorporate_discounting:
            self._update_values_with_discounting() # if not incorp_growth but still want to incorp discounting

    @classmethod
    def from_cashflow(cls,
                      cashflow, # TO DO: how do you type-hint the class itself?
                      cashflow_type: Optional[str] = None,
                      name: Optional[str] = None
                      ): # TO DO: how do you type-hint the class itself?:
        cashflow_type = cashflow_type if cashflow_type is not None else cashflow._cashflow_type
        name = name if name is not None else cashflow.name
        date_range = cashflow.date_range
        values = cashflow._values
        outflow = cashflow._outflow
        return cls(cashflow_type=cashflow_type, name=name, date_range=date_range,
                   values=values, outflow=outflow)


    @property
    def date_range(self) -> pd.date_range:
        freq = hp.FREQ_MAP.get(self.freq, self.freq)
        date_range = pd.date_range(
            start=self.start_dt,
            end=self.end_dt,
            freq=freq,
            normalize=True
        )
        return date_range


    @property
    def days_from_start(self) -> List[int]:
        """
        Get self.date_range expressed as days from start_dt.
        TO DO: Think about exposing period_resolution == '1D'
        """
        n_periods = [(x - self.date_range.min())/pd.Timedelta('1D')
                     for x in self.date_range]
        return n_periods


    @property
    def cash_flows_df(self) -> pd.DataFrame:
        """A pandas dataframe representing the cashflows from the income stream.
        """
        cash_flows = pd.DataFrame(
            index=self.date_range,
            data=self._values,
            columns=[self.name]
        )

        return cash_flows


    def plot_cash_flows(self, cumulative: bool = True, **kwargs) -> None:
        if cumulative:
            to_plt = (
                self.cash_flows_df
                .resample('d')
                .mean()
                .cumsum()
                .fillna(method='ffill')
            )
            chart_type = 'line'
        else:
            to_plt = self.cash_flows_df
            chart_type = 'bar'

        to_plt.plot(kind=chart_type, **kwargs)


    @property
    def _local_vol_fn(self) -> Callable:
        # Should be overwritten by subclasses where applicable;
        # Currently, returns the number itself, equivalent to no local vol
        return lambda x: np.random.normal(x, scale=0.0)


    def _get_growth_series(self) -> pd.Series:
        growth_factors = self.growth_series.growth_series
        full_index = pd.DatetimeIndex.union(
            self.growth_series.date_range,
            self.date_range
        )
        growth_series = (
            growth_factors
            .reindex(full_index, method='pad') # propogate growth vals forward
            .fillna(1) # observations pre-first growth date should be 0 growth
        )
        # Align the series of growth factors w/ original date_range
        aligned_growth_series = growth_series.resample(self.freq).pad()
        return aligned_growth_series


    def _add_local_vol(self, series: pd.Series,
                       fn: Optional[Callable] = None
                       ) -> pd.Series:
        fn = fn if fn else self._local_vol_fn
        return series.apply(fn)


    def get_growth_path(self, return_df: bool = False) -> Optional[pd.DataFrame]:
        initial_series = pd.Series(self._initial_values, index=self.date_range)
        growth_series = self._get_growth_series()
        growth_series_with_vol = self._add_local_vol(growth_series)
        updated_values = initial_series.multiply(growth_series_with_vol, axis=0)
        if return_df:
            to_return = pd.DataFrame(
                index=self.date_range,
                data={
                    self.name: self._initial_values,
                    f'{self.name}_w_growth': updated_values.values
                    }
                )
        else:
            to_return = updated_values

        return to_return

    def update_values_with_growth(self) -> None:
        updated_values = self.get_growth_path()
        self._values = updated_values
        if self._incorporate_discounting:
            self._update_values_with_discounting()

    def get_discounted_values(self, yearly_discount_rate: float = 0.02
                             ) -> pd.Series:
        vals = self._values.copy()
        n_periods = (vals.index - vals.index.min())/pd.Timedelta('1Y')
        discount_factors = pd.Series(
            data=[(1 + yearly_discount_rate)**x for x in n_periods],
            index=vals.index
        )
        discounted_vals = vals.divide(discount_factors)

        return discounted_vals


    def _update_values_with_discounting(self, **kwargs) -> None:
        self._values = self.get_discounted_values(self._yearly_discount_rate)
