import numpy as np
import pandas as pd
import random

from gameplan.cashflows import CashFlow
from gameplan.gp_collections import CashFlowCollection, Collection
from gameplan.contributions import Contribution
from gameplan.growth.asset_returns import AssetReturns


class Asset():
    RETURNS = AssetReturns()

    def __init__(self, asset_type, initial_balance, date_range):
        self.asset_type = asset_type
        self.initial_balance = initial_balance
        self.credits_and_debits = CashFlowCollection(objects={})
        init_contrib = Contribution(
            contribution_label='initial_balance',
            amount=initial_balance,
            start_dt=pd.datetime.today(),
            recurring=False
        )
        self.add_contribution(init_contrib)
        self.date_range = date_range


    def add_contribution(self, contribution, label=None, if_exists='error'):
        label = label if label else contribution.name
        self.credits_and_debits.add_object(contribution, label, if_exists)

    # I'm very skeptical this needs to exist rather than combining w/ above
    # Keeping for now cause don't want to rename/cleanup add_contribution
    def add_debit(self, debit, label=None, if_exists='error'):
        label = label if label else debit.name
        self.credits_and_debits.add_object(debit, label, if_exists)

    def _get_compound_factors(self, date_diffs, *args, **kwargs):
        raise NotImplementedError

    @property
    def value_through_time(self):
        full_index = pd.DatetimeIndex.union(
            self.credits_and_debits.total.index,
            self.date_range
        )
        t = (
            self.credits_and_debits.total
            .reindex(index=full_index, fill_value=0)
            .resample('D').sum() # downsample to daily)
        ) # get a daily view of credits_and_debits over the entire self.date_range
        date_diffs = t.index.to_series().diff()
        compound_factors = self._get_compound_factors(date_diffs)

        totals = []
        total = 0
        for x, r in zip(t.values, compound_factors.values):
            r = r if pd.notnull(r) else 0
            total = x + r * total
            totals.append(total)

        return pd.Series(data=totals, index=t.index, name='total_value')


class CashSavings(Asset):
    # How much cash do you currently have across all of your checking and savings accounts? $_______
    # What proportion of your take-home pay do you expect to go to these accounts over the course of the next few years (on average)? ______%
    DEFAULT_DATE_RANGE = pd.date_range(
        start=pd.datetime.today().date(),
        end=pd.datetime.today().date() + pd.DateOffset(years=20),
        freq='D'
    )
    def __init__(self, initial_balance=0, annualized_interest_rate=0.0,
                 date_range=DEFAULT_DATE_RANGE):
        super().__init__(
            asset_type='cash_savings',
            initial_balance=initial_balance,
            date_range = date_range
            )
        self.annualized_interest_rate = annualized_interest_rate


    def _get_compound_factors(self, date_diffs):
        return date_diffs.apply(
            lambda x: np.e**(self.annualized_interest_rate * x.days / 365.25)
            )


class Equity(Asset): # should be type Investment
    DEFAULT_DATE_RANGE = pd.date_range(
        start=pd.datetime.today().date(),
        end=pd.datetime.today().date() + pd.DateOffset(years=20),
        freq='B'
    )

    def __init__(self, ticker='SPY', init_value=1, date_range=DEFAULT_DATE_RANGE):
        super().__init__(
            asset_type='equity',
            initial_balance=init_value,
            date_range = date_range
            )
        self.returns_series = Asset.RETURNS.get_returns_series(
            asset_type='equity',
            ticker=ticker
            )

    def _get_compound_factors(self, date_diffs):
        returns_path = self.returns_series.returns_df['sim_1'] # just take 1st sim
        return (returns_path
                .shift(1)
                .reindex(date_diffs.index)
                .resample('D')
                .first()
                .fillna(1.0)
                )


class Assets(Collection):
    def __init__(self, collection_type=Asset, objects={}):
        # TO DO: Should signature be assets= instead of objects=?
        if not issubclass(collection_type, Asset):
            raise ValueError(f"collection_type must be of type {Asset}")

        asset_objects = (
            hp.combine_list_of_dicts(objects) if isinstance(objects, list)
            else objects
            )
        super().__init__(collection_type, asset_objects)


    def generate_path_df(self):
        df = pd.DataFrame(
            { k: v.value_through_time for k,v in self.contents.items() }
        ).fillna(method='bfill')

        df['total'] = df.sum(axis=1)

        return df

    def generate_value_path(self):
        return self.generate_path_df()['total']

    @property
    def current_value(self):
        today = pd.datetime.today().date()
        return self.generate_value_path()[today:].iloc[0]
