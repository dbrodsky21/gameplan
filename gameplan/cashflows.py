import pandas as pd
import numpy as np

import gameplan.helpers as hp


class CashFlow():
    def __init__(self, cashflow_type, name, amount, freq, start_dt, end_dt=None):
        """

        """
        self._cashflow_type = cashflow_type
        self.name = name
        self.amount = amount
        self.freq=freq
        self.start_dt = start_dt
        self.end_dt = (
            end_dt if end_dt
            else start_dt + pd.DateOffset(years=1)
        )

    @property
    def cash_flows(self):
        """A pandas dataframe representing the cashflows from the income stream.
        """
        freq = hp.FREQ_MAP.get(self.freq, self.freq)
        date_range = pd.date_range(
            start=self.start_dt,
            end=self.end_dt,
            freq=freq,
            normalize=True
        )

        cash_flows = pd.DataFrame(
            index=date_range,
            data=[self.amount] * len(date_range),
            columns=[self.name]
        )

        return cash_flows


    def plot_cash_flows(self, cumulative=True, **kwargs):
        if cumulative:
            to_plt = (
                self.cash_flows
                .resample('d')
                .mean()
                .cumsum()
                .fillna(method='ffill')
            )
            chart_type = 'line'
        else:
            to_plt = self.cash_flows
            chart_type = 'bar'

        to_plt.plot(kind=chart_type, **kwargs)
