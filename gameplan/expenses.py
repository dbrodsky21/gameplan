import pandas as pd
import numpy as np

import gameplan.helpers as hp


"""
General Expense Module
What’s the expense?
_______
How much is it? ______
What type of expense is it?
One-time
Recurring
When?
"""
class Expense():
    def __init__(self, expense_type, amount, recurring, start_dt, freq=None,
                 end_dt=None):
        """

        """
        self.expense_type = expense_type
        self.amount = amount
        self.recurring = recurring
        self.start_dt = start_dt
        self.freq=freq
        self.end_dt = start_dt if not recurring else (
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
            data=[-self.amount] * len(date_range), # Note the negative sign
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


class Rent(Expense):
    def __init__(self, amount, start_dt=pd.datetime.today(), freq='MS',
                 end_dt=pd.datetime.today() + pd.DateOffset(years=1)):
        super().__init__(
            expense_type='rent',
            amount=amount,
            recurring=True,
            start_dt=start_dt,
            freq=freq,
            end_dt=end_dt
        )


class Utilities(Expense):
    def __init__(self, amount, start_dt=pd.datetime.today(), freq='MS',
                 end_dt=pd.datetime.today() + pd.DateOffset(years=1)):
        super().__init__(
            expense_type='utilities',
            amount=amount,
            recurring=True,
            start_dt=start_dt,
            freq=freq,
            end_dt=end_dt
        )
