import pandas as pd
import numpy as np

from gameplan.cashflows import CashFlow


class Expense(CashFlow):
    def __init__(self, expense_type, amount, recurring, start_dt, freq=None,
                 end_dt=None):
        super().__init__(
            cashflow_type='expense',
            name=expense_type,
            amount=amount,
            start_dt=start_dt,
            freq=freq,
        )
        self.recurring = recurring
        self.end_dt = start_dt if not recurring else (
            end_dt if end_dt
            else start_dt + pd.DateOffset(years=1)
        )


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
