import pandas as pd
import numpy as np

from gameplan.cashflows import CashFlow
from gameplan.gp_collections import CashFlowCollection


class Contribution(CashFlow):
    def __init__(self, contribution_label, date_range=None, values=None,
                 amount=None, recurring=None, freq=None, start_dt=None,
                 end_dt=None, incorporate_growth=False):
        super().__init__(
            cashflow_type='contribution',
            name=contribution_label,
            date_range=date_range,
            values=values,
            amount=amount,
            recurring=recurring,
            freq=freq,
            start_dt=start_dt,
            end_dt=end_dt,
            outflow=False,
            incorporate_growth=incorporate_growth
        )

    @classmethod
    def from_income_stream(cls, income_stream, pct=1.0, label=None,
                           max_amt=None, max_amt_freq=None):
        label = (
            label if label is not None
            else f"{pct:.0%} Contribution from {income_stream.name}"
        )
        date_range = income_stream.date_range
        # Need to consolidate w/ deduction logic, below; exact same
        if not any([max_amt, max_amt_freq]):
            values = [ pct * x for x in income_stream._values ]
        elif all([max_amt, max_amt_freq]):
            n_pay_periods = income_stream.salary_df.resample(
                max_amt_freq,
                label='left',
                loffset='d'
                ).count()
            cap = pd.Series(index=n_pay_periods.index, data=max_amt)
            max_amt_series = pd.Series(cap / n_pay_periods.iloc[:, 0])
            max_amt_series= max_amt_series.reindex(date_range, method='ffill')
            zipped = zip(income_stream._values, max_amt_series.values)
            values = [ min(pct * x, y) for x, y in zipped ]
        else:
            raise ValueError("Need either both or neither of max_amt params to be None.")

        return cls(contribution_label=label, date_range=date_range,
                   values=values)


class Deduction(CashFlow):
    def __init__(self, deduction_label, date_range=None, values=None,
                 amount=None, recurring=None, freq=None, start_dt=None,
                 end_dt=None, incorporate_growth=False):
        super().__init__(
            cashflow_type='deduction',
            name=deduction_label,
            date_range=date_range,
            values=values,
            amount=amount,
            recurring=recurring,
            freq=freq,
            start_dt=start_dt,
            end_dt=end_dt,
            outflow=True,
            incorporate_growth=incorporate_growth
        )

    @classmethod
    def from_income_stream(cls, income_stream, pct=1.0, label=None,
                           max_amt=None, max_amt_freq=None):
        label = (
            label if label is not None
            else f"{pct:.0%} Deduction from {income_stream.name}"
        )
        date_range = income_stream.date_range
        # Need to consolidate w/ contribution logic, above; exact same
        if not any([max_amt, max_amt_freq]):
            values = [ pct * x for x in income_stream._values ]
        elif all([max_amt, max_amt_freq]):
            n_pay_periods = income_stream.salary_df.resample(
                max_amt_freq,
                label='left',
                loffset='d'
                ).count()
            cap = pd.Series(index=n_pay_periods.index, data=max_amt)
            max_amt_series = pd.Series(cap / n_pay_periods.iloc[:, 0])
            max_amt_series= max_amt_series.reindex(date_range, method='ffill')
            zipped = zip(income_stream._values, max_amt_series.values)
            values = [ min(pct * x, y) for x, y in zipped ]
        else:
            raise ValueError("Need either both or neither of max_amt params to be None.")

        return cls(deduction_label=label, date_range=date_range,
                   values=values)


class Contributions(CashFlowCollection):
    def __init__(self, contributions={}):
        super().__init__(collection_type=Contribution, objects=contributions)
