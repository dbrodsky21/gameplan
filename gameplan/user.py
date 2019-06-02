import pandas as pd
import numpy as np
import shelve
import zlib

from gameplan import paths

class User():
    def __init__(self, email):
        self.email = email.lower()
        self.age = None
        self.family_status = None # eventually, family_status object can house marital status + children + etc.
        self.education = None # education object includes highest level of education, which college, etc.
        self.credit_score = None
        self.health = None # health object can include health_status = ['good', 'bad', etc.], insurance = [yes/no]
        self.income_streams = None # includes salary, etc.
        self.expenses = None
        self.assets = None
        self.liabilities = None

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
