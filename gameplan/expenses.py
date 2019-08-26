import pandas as pd
import numpy as np

from gameplan.cashflows import CashFlow
from gameplan.collections import CashFlowCollection


class Expense(CashFlow):
    def __init__(self, expense_type, amount, recurring, start_dt, freq=None,
                 end_dt=None):
        super().__init__(
            cashflow_type='expense',
            name=expense_type,
            amount=amount,
            start_dt=start_dt,
            freq=freq,
            recurring=recurring,
            outflow=True
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


class Expenses(CashFlowCollection):
    def __init__(self, expenses={}):
        super().__init__(collection_type=Expense, objects=expenses)
