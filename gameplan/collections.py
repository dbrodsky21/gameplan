import pandas as pd
import numpy as np

import gameplan.helpers as hp
from gameplan.contributions import Contribution
from gameplan.income_streams import IncomeStream
from gameplan.expenses import Expense


class Collection():
    def __init__(self, collection_type, objects={}):
        self.collection_type = collection_type
        if [x for x in objects.values() if not isinstance(x, collection_type)]:
            raise ValueError(f"All objects must be of type {collection_type}")
        self.contents = objects


    def add_object(self, object, label=None, if_exists='error'):
        if not isinstance(object, self.collection_type):
            raise ValueError(f"Object must be a {self.collection_type} object.")

        default_label = f"item_{len(self.contents) + 1}"
        label = label if label else getattr(object, 'name', default_label)
        if label in self.contents:
            error_message = (
                f"Label '{label}' already exists. "
                f"If you want to overwrite it, set if_exists to 'overwrite'"
            )
            warning_message = (
                f"Label '{label}' already exists. Will overwrite."
            )
            if if_exists == 'error':
                raise ValueError(error_message)
            elif if_exists == 'overwrite':
                warnings.warn(warning_message)
            else:
                raise ValueError(error_message)

        self.contents[label] = object


    def remove_object(self, label, verbose=True):
        if label in self.contents:
            del self.contents[label]
        elif verbose:
            warnings.warn(f"No object w/ label '{label}' exists.")


    def _get_totals_df(self, to_total, warn=True, totals_col_label='total'):
        "Each collection subclass should use this to create a totals_df property."
        if not self.contents:
            if warn: warnings.warn('This Collection is empty.')
            return None
        coll_contents = [getattr(x, to_total) for x in self.contents.values()]
        df = pd.concat(coll_contents, axis=1).fillna(0)
        df[totals_col_label] = df.sum(axis=1)

        return df

    def _get_total(self, to_total, totals_col_label='total'):
        "Each collection subclass should use this to create a totals_df property."
        totals_df = self._get_totals_df(to_total, totals_col_label=totals_col_label)
        return totals_df[totals_col_label] if totals_df is not None else None



class IncomeStreams(Collection):
    def __init__(self, income_streams={}):
        super().__init__(collection_type=IncomeStream, objects=income_streams)

    @property
    def income_streams_df(self):
        """Think about temporal aspect here too"""
        return self._get_totals_df(
                    to_total='cash_flows_df',
                    totals_col_label='total_income'
                    )

    @property
    def total_income(self):
        return self._get_total(
                    to_total='cash_flows_df',
                    totals_col_label='total_income'
                    )


class Expenses(Collection):
    def __init__(self, expenses={}):
        super().__init__(collection_type=Expense, objects=expenses)

    @property
    def expenses_df(self):
        """Think about temporal aspect here too"""
        return self._get_totals_df(
                    to_total='cash_flows_df',
                    totals_col_label='total_expenses'
                    )

    @property
    def total_expenses(self):
        return self._get_total(
                    to_total='cash_flows_df',
                    totals_col_label='total_expenses'
                    )


class Contributions(Collection):
    def __init__(self, contributions={}):
        super().__init__(collection_type=Contribution, objects=contributions)

    @property
    def contributions_df(self):
        """Think about temporal aspect here too"""
        return self._get_totals_df(
                    to_total='cash_flows_df',
                    totals_col_label='total_contributions'
                    )

    @property
    def total_contributions(self):
        return self._get_total(
                    to_total='cash_flows_df',
                    totals_col_label='total_contributions'
                    )
