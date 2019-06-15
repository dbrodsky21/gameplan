import pandas as pd
import numpy as np

from gameplan.cashflows import CashFlow


class IncomeStream(CashFlow):
    def __init__(self, income_type, amount, freq, start_dt, end_dt=None):
        super().__init__(
            cashflow_type='income',
            name=income_type,
            amount=amount,
            freq=freq,
            start_dt=start_dt,
            end_dt=end_dt,
            recurring=True
        )


class Salary(IncomeStream):
    def __init__(self, paycheck_amt, payday_freq, next_paycheck_dt=None,
                 last_paycheck_dt=None):

        start_dt = (
            next_paycheck_dt if next_paycheck_dt
            else hp.get_offset_date(payday_freq)
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
        return self.cash_flows_df.resample('365D').sum().values[0][0]
