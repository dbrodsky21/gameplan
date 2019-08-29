import pandas as pd
import numpy as np

import gameplan.helpers as hp


class CashFlow():
    DEFAULT_END_DT_OFFSET = pd.DateOffset(years=20)

    def __init__(self, cashflow_type, name, date_range=None, values=None,
                 amount=None, recurring=None, freq=None, start_dt=None,
                 end_dt=None, outflow=False):
        """
        """
        self._cashflow_type = cashflow_type
        self.name = name
        if date_range is not None:
            self.start_dt = date_range.min()
            self.end_dt = date_range.max()
            self.freq = date_range.freq
        else:
            self.start_dt = start_dt
            self.end_dt = start_dt if not recurring else (
                end_dt if end_dt
                else start_dt + DEFAULT_END_DT_OFFSET
            )
            self.freq=freq

        self.amount = amount
        self._initial_values = values if values is not None else (
            [amount] * len(self.date_range)
        )
        self._values = self._initial_values # We may want to change values, e.g. growth in salary/expenses, but want to still have a record of original _values
        self._outflow = outflow


    @classmethod
    def from_cashflow(cls, cashflow, cashflow_type=None, name=None):
        cashflow_type = cashflow_type if cashflow_type is not None else cashflow._cashflow_type
        name = name if name is not None else cashflow.name
        date_range = cashflow.date_range
        values = cashflow._values
        outflow = cashflow._outflow
        return cls(cashflow_type=cashflow_type, name=name, date_range=date_range,
                   values=values, outflow=outflow)


    @property
    def date_range(self):
        freq = hp.FREQ_MAP.get(self.freq, self.freq)
        date_range = pd.date_range(
            start=self.start_dt,
            end=self.end_dt,
            freq=freq,
            normalize=True
        )
        return date_range

    @property
    def cash_flows_df(self):
        """A pandas dataframe representing the cashflows from the income stream.
        """
        cash_flows = pd.DataFrame(
            index=self.date_range,
            data=self._values,
            columns=[self.name]
        )

        return cash_flows


    def plot_cash_flows(self, cumulative=True, **kwargs):
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
    def _growth_fn(self):
        # Should be overwritten by subclasses where applicable;
        # Currently, return 1 is equivalent to no growth
        return 1


    def _get_growth_series(self, start_dt=None, end_dt=None,
                           growth_freq=None, growth_fn=None):
        start_dt = start_dt if start_dt else self.start_dt
        end_dt = end_dt if end_dt else self.end_dt
        growth_freq = growth_freq if growth_freq else self.growth_freq
        growth_date_range = pd.date_range(start=start_dt, end=end_dt,
                                          freq=growth_freq)
        growth_fn = growth_fn if growth_fn else self._growth_fn
        growth_factors = pd.Series(index=growth_date_range).apply(
            growth_fn
            )
        full_index = pd.DatetimeIndex.union(
            growth_date_range,
            self.date_range
        )
        growth_series = (
            growth_factors
            .reindex(full_index, fill_value=1)
            .cumprod()
        )

        # Algin the series of growth factors w/ original date_range
        aligned_growth_series = growth_series.resample(self.freq).pad()

        return aligned_growth_series

    def get_growth_path(self, return_df=False, **kwargs):
        initial_series = pd.Series(self._initial_values, index=self.date_range)
        growth_series = self._get_growth_series(**kwargs)
        updated_values = initial_series.multiply(growth_series, axis=0)
        if return_df:
            to_return = pd.DataFrame(
                index=self.date_range,
                values=[self._initial_values, updated_values],
                columns=[self.name, f'{self.name}_w_growth`']
                )
        else:
            to_return = updated_values

        return to_return

    def update_values_with_growth(self, **kwargs):
        updated_values = self.get_growth_path(**kwargs)
        self._values = updated_values
