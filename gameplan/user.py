import pandas as pd
import numpy as np
import shelve
import warnings
import zlib

from gameplan import paths, income_streams, expenses

class User():
    def __init__(self, email):
        self.email = email.lower()
        self.age = None
        self.family_status = None # eventually, family_status object can house marital status + children + etc.
        self.education = None # education object includes highest level of education, which college, etc.
        self.credit_score = None
        self.health = None # health object can include health_status = ['good', 'bad', etc.], insurance = [yes/no]
        self.income_streams = [] # includes salary, etc.
        self.expenses = []
        self.assets = []
        self.liabilities = []

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
            if verbose:
                print("Progress Saved!")

    def add_income_stream(self, income_stream):
        if not isinstance(income_stream, income_streams.IncomeStream):
            raise ValueError("income_stream must be a gameplan.income_streams.IncomeStream object")

        self._income_streams = self.income_streams.append(income_stream)

    def add_expense(self, expense):
        if not isinstance(expense, expenses.Expense):
            raise ValueError("expense must be a gameplan.expenses.Expense object")

        self._expenses = self.expenses.append(expense)


    @property
    def income_streams_df(self):
        """Think about temporal aspect here too"""
        if not self.income_streams:
            warnings.warn('No income streams associated w/ user')
            return None
        df = pd.concat([x.cash_flows_df for x in self.income_streams], axis=1)
        df['total_income'] = df.sum(axis=1)

        return df

    @property
    def total_income(self):
        df = self.income_streams_df
        return self.income_streams_df.total_income if df is not None else None

    @property
    def expenses_df(self):
        """Think about temporal aspect here too"""
        if not self.expenses:
            warnings.warn('No expenses associated w/ user')
            return None
        df = pd.concat([x.cash_flows_df for x in self.expenses], axis=1)
        df['total_expenses'] = df.sum(axis=1)

        return df

    @property
    def total_expenses(self):
        df = self.expenses_df
        return self.expenses_df.total_expenses if df is not None else None


    @property
    def cash_flows_df(self):
        df = pd.concat([
            self.income_streams_df,
            -self.expenses_df if self.expenses_df is not None else None
        ], axis=1).fillna(0)

        return df

    def agg_cash_flows(self, freq):
        return self.cash_flows_df.resample(freq).sum()

    @property
    def net_cash_flow(self):
        df = self.cash_flows_df
        return df['total_income'] + df['total_expenses']

    def agg_net_cash_flows(self, freq):
        return self.net_cash_flow.resample(freq).sum()

    # @property
    # def net_worth(self):
    #     """How to handle the temporal aspect of this?"""
    #     return self.assets + self.liabilities
