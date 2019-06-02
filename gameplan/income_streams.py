import pandas as pd
import numpy as np

import gameplan.helpers as hp


class IncomeStream():
    def __init__(self, income_type, amount, freq, first_pmt_dt,
                 last_pmt_dt=None):
        self.income_type = income_type
        self.amount = amount
        self.freq = freq
        self.first_pmt_dt = first_pmt_dt
        self.last_pmt_dt = (
            last_pmt_dt if last_pmt_dt
            else first_pmt_dt + pd.DateOffset(years=1)
        )

    @property
    def cash_flows(self):
        """A pandas dataframe representing the cashflows from the income stream.
        """
        freq = hp.FREQ_MAP.get(self.freq, self.freq)
        date_range = pd.date_range(
            start=self.first_pmt_dt,
            end=self.last_pmt_dt,
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

        first_pmt_dt = (
            next_paycheck_dt if next_paycheck_dt
            else hp.get_next_date_offset(payday_freq)
        )
        # TO DO: add validation that first/last dts aren't conflicting
        last_pmt_dt = (
            last_paycheck_dt if last_paycheck_dt
            else first_pmt_dt + pd.DateOffset(years=1)
        )

        super().__init__(
            income_type='salary',
            amount=paycheck_amt,
            freq=payday_freq,
            first_pmt_dt=first_pmt_dt,
            last_pmt_dt=last_pmt_dt
        )


    @property
    def annualized_salary(self):
        """TO DO: refactor"""
        return self.cash_flows.resample('365D').sum().values[0][0]
