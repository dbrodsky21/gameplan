import pandas as pd
import numpy as np

from gameplan.cashflows import CashFlow
from gameplan.collections import CashFlowCollection


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
    def from_income_stream(cls, income_stream, pct=1.0, label=None):
        label = (
            label if label is not None
            else f"{pct:.0%} Contribution from {income_stream.name}"
        )
        date_range = income_stream.date_range
        values = [pct * x for x in income_stream._values]
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
    def from_income_stream(cls, income_stream, pct=1.0, label=None):
        label = (
            label if label is not None
            else f"{pct:.0%} Deduction from {income_stream.name}"
        )
        date_range = income_stream.date_range
        values = [pct * x for x in income_stream._values]
        return cls(deduction_label=label, date_range=date_range,
                   values=values)


class Contributions(CashFlowCollection):
    def __init__(self, contributions={}):
        super().__init__(collection_type=Contribution, objects=contributions)
