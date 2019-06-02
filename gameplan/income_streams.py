import pandas as pd
import numpy as np

import gameplan.helpers as hp


class IncomeStream():
    def __init__(self, income_type, amount, freq, start_dt, end_dt=None):
        self.income_type = income_type
        self.amount = amount
        self.freq = freq
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
            columns=[self.income_type]
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


class Salary(IncomeStream):
    def __init__(self, paycheck_amt, payday_freq, next_paycheck_dt=None,
                 last_paycheck_dt=None):

        start_dt = (
            next_paycheck_dt if next_paycheck_dt
            else hp.get_next_date_offset(payday_freq)
        )
        # TO DO: add validation that first/last dts aren't conflicting
        end_dt = (
            last_paycheck_dt if last_paycheck_dt
            else start_dt + pd.DateOffset(years=1)
        )

        super().__init__(
            income_type='salary',
            amount=paycheck_amt,
            freq=payday_freq,
            start_dt=start_dt,
            end_dt=end_dt
        )


    @property
    def annualized_salary(self):
        """TO DO: refactor"""
        return self.cash_flows.resample('365D').sum().values[0][0]
