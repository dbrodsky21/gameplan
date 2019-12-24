import pandas as pd
import numpy as np
import warnings

import gameplan.helpers as hp
# from gameplan.assets import Asset
from gameplan.cashflows import CashFlow
# from gameplan.contributions import Contribution
# from gameplan.income_streams import IncomeStream
# from gameplan.expenses import Expense


class Collection():
    def __init__(self, collection_type, objects={}):
        self.collection_type = collection_type
        if [x for x in objects.values() if not isinstance(x, collection_type)]:
            raise ValueError(f"All objects must be of type {collection_type}")
        self.contents = objects


    @property
    def _collection_type_str(self):
        return hp.to_snake_case(self.collection_type.__name__)


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


class CashFlowCollection(Collection):
    """
    TO DO: Needs to be able to be instantiated from other instances of
    CashFlowCollection, e.g. IncomeStreams, Expenses, etc.
    """
    def __init__(self, collection_type=CashFlow, objects={},
                 totals_col_label=None):
        if not issubclass(collection_type, CashFlow):
            raise ValueError(f"collection_type must be of type {CashFlow}")

        cf_objects = (
            hp.combine_list_of_dicts(objects) if isinstance(objects, list)
            else objects
            )
        super().__init__(collection_type, cf_objects)
        self.totals_col_label = (
            totals_col_label if totals_col_label
            else f'total_net_{self._collection_type_str}'
            )


    @property
    def inflows(self):
        return {k: v for k,v in self.contents.items() if not v._outflow}

    @property
    def outflows(self):
        return {k: v for k,v in self.contents.items() if v._outflow}

    @property
    def as_df(self):
        return self._get_totals_df()

    def agg_cash_flows(self, freq):
        return self.as_df.resample(freq).sum()

    @property
    def total(self):
        return getattr(self.as_df, self.totals_col_label, None)


    def get_total_as_cashflow(self, freq, name=None):
        if pd.Series(self.total).empty:
            return None
        total = self.total.resample(freq).sum()
        label = name if name else self.totals_col_label
        cf = CashFlow(
                cashflow_type=self.collection_type,
                name=label,
                date_range=total.index,
                values=total.values
                )
        return cf

    def _get_totals_df(self, warn=True):
        "Each collection subclass should use this to create a totals_df property."
        if not self.contents:
            if warn: warnings.warn('This Collection is empty.')
            return None
        inflows = [x.cash_flows_df for x in self.inflows.values()]
        outflows = [-x.cash_flows_df for x in self.outflows.values()]
        df = pd.concat(inflows + outflows, axis=1).fillna(0)
        totals_col_label = self.totals_col_label
        df[totals_col_label] = df.sum(axis=1)

        return df
