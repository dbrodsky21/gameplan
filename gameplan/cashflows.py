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
        self._values = values if values is not None else (
            [amount] * len(self.date_range)
        )
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
