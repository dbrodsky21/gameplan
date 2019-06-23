import pandas as pd
import numpy as np
import shelve
import warnings
import zlib

from gameplan.assets import Asset
from gameplan.cashflows import CashFlow
from gameplan.collections import Collection, CashFlowCollection, IncomeStreams, Expenses
from gameplan import paths

class User():
    def __init__(self, email):
        self.email = email.lower()
        self.age = None
        self.family_status = None # eventually, family_status object can house marital status + children + etc.
        self.education = None # education object includes highest level of education, which college, etc.
        self.credit_score = None
        self.health = None # health object can include health_status = ['good', 'bad', etc.], insurance = [yes/no]
        self.income_streams = IncomeStreams(income_streams={}) # includes salary, etc.
        self.expenses = Expenses(expenses={})
        self.assets = Collection(collection_type=Asset, objects={})
        # self.liabilities = Collection(collection_type=income_streams.IncomeStream, objects={})

        self.save_user()

    @property
    def user_id(self):
        return self.get_user_id(self.email)

    @property
    def retirement_age(self):
        return 65

    @property
    def life_expectancy(self):
        return 95

    @staticmethod
    def get_user_id(email):
        # Need to do this garbage to make the hash deterministic
        # Not clear hashing is even worthwhile if its deterministic
        return str(zlib.adler32(email.encode('utf-8')) & 0xffffffff)

    def save_user(self, verbose=False):
        """"TO DO: This should keep track of where in the process the user is"""
        with shelve.open(paths.USERS_DB_PATH, 'c') as user_db:
            user_db[self.user_id] = self
            if verbose: print("Progress Saved!")


    def add_income_stream(self, income_stream, label=None, if_exists='error'):
        self.income_streams.add_object(income_stream, label, if_exists)


    def add_expense(self, expense, label=None, if_exists='error'):
        self.expenses.add_object(expense, label, if_exists)


    def add_asset(self, asset, label=None, if_exists='error'):
        self.assets.add_object(asset, label, if_exists)


    @property
    def all_cashflows(self):
        return CashFlowCollection(
            collection_type=CashFlow,
            objects=[self.income_streams.contents, self.expenses.contents]
        )


    # @property
    # def net_worth(self):
    #     """How to handle the temporal aspect of this?"""
    #     return self.assets + self.liabilities
