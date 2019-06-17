import pandas as pd
import numpy as np
import warnings

from gameplan.cashflows import CashFlow
from gameplan.collections import Collection


class Contribution(CashFlow):
    def __init__(self, contribution_label, date_range=None, values=None, amount=None, recurring=None,
                 freq=None, start_dt=None, end_dt=None):
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
        )

    @classmethod
    def from_income_stream(cls, income_stream, pct=1.0, label=None):
        label = (
            label if label is not None
            else f"{pct:.0%} Contribution from {income_stream.name}"
        )
        date_range = income_stream.date_range
        values = [pct * x for x in income_stream.values]
        return cls(contribution_label=label, date_range=date_range,
                   values=values)


class Asset():
    def __init__(self, asset_type):
        self.asset_type = asset_type

# How much cash do you currently have across all of your checking and savings accounts? $_______
# What proportion of your take-home pay do you expect to go to these accounts over the course of the next few years (on average)? ______%

class CashSavings(Asset):
    def __init__(self, initial_balance=0, annualized_interest_rate=0.0):
        super().__init__(asset_type='cash_savings')
        self.initial_balance = initial_balance
        self.annualized_interest_rate = annualized_interest_rate
        self.contributions = Collection(collection_type=Contribution, objects={})

    @property
    def all_contributions_df(self):
        contrib_cashflows = [
            x.cash_flows_df for x in self.contributions.contents.values()
        ]
        df = (
            pd.concat(contrib_cashflows, axis=1)
            .fillna(0)
            .cumsum()
        )
        df['total_contributions'] = df.sum(axis=1)
        return df
