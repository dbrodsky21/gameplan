import pandas as pd
import numpy as np

from gameplan.cashflows import CashFlow
from gameplan.collections import CashFlowCollection


class Expense(CashFlow):
    def __init__(self, expense_type, amount=None, recurring=None, start_dt=None, freq=None,
                 end_dt=None, date_range=None, values=None, pretax=False):
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
        )
        self.pretax=pretax

class Rent(Expense):
    def __init__(self, amount, start_dt=pd.datetime.today(), freq='MS',
                 end_dt=pd.datetime.today() + pd.DateOffset(years=20)):
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
                 end_dt=pd.datetime.today() + pd.DateOffset(years=20)):
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

    @property
    def pretax(self):
        return {k: v for k,v in self.contents.items() if v.pretax}

    @property
    def post_tax(self):
        return {k: v for k,v in self.contents.items() if not v.pretax}
