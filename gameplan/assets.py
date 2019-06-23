import pandas as pd
import numpy as np

from gameplan.cashflows import CashFlow
from gameplan.collections import Contributions


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
