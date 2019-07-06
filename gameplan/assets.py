import pandas as pd
import numpy as np

from gameplan.cashflows import CashFlow
from gameplan.collections import Contributions
from gameplan.contributions import Contribution


class Asset():
    def __init__(self, asset_type):
        self.asset_type = asset_type


class CashSavings(Asset):
    # How much cash do you currently have across all of your checking and savings accounts? $_______
    # What proportion of your take-home pay do you expect to go to these accounts over the course of the next few years (on average)? ______%

    def __init__(self, initial_balance=0, annualized_interest_rate=0.0):
        super().__init__(asset_type='cash_savings')
        self.initial_balance = initial_balance
        self.annualized_interest_rate = annualized_interest_rate
        self.contributions = Contributions(contributions={})
        init_contrib = Contribution(
            contribution_label='initial_balance',
            amount=initial_balance,
            start_dt=pd.datetime.today(),
            recurring=False
        )
        self.add_contribution(init_contrib)


    def add_contribution(self, contribution, label=None, if_exists='error'):
        label = label if label else contribution.name
        self.contributions.add_object(contribution, label, if_exists)


    @property
    def value_through_time(self):
        t = self.contributions.total
        date_diffs = t.index.to_series().diff()
        compound_factors = date_diffs.apply(
            lambda x: np.e**(self.annualized_interest_rate * x.days / 365.25)
            )

        totals = []
        total = 0
        for x, r in zip(t.values, compound_factors.values):
            r = r if pd.notnull(r) else 0
            total = x + r * total
            totals.append(total)

        return pd.Series(data=totals, index=t.index, name='total_value')
