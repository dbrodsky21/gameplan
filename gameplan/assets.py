import numpy as np
import pandas as pd
import random

import fecon236.prob.sim as fe_sim

from gameplan.cashflows import CashFlow
from gameplan.gp_collections import CashFlowCollection, Collection
from gameplan.contributions import Contribution


class Asset():
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

    def simulate_path(self, **kwargs):
        raise NotImplementedError

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


    def simulate_path(self):
        """There's at least some stochasticity here around interest rate"""
        return self.value_through_time


class Equity(Asset): # should be type Investment
    DEFAULT_DATE_RANGE = pd.date_range(
        start=pd.datetime.today().date(),
        end=pd.datetime.today().date() + pd.DateOffset(years=20),
        freq='B'
    )
    DEFAULT_MU = fe_sim.SPXmean
    DEFAULT_SIGMA = fe_sim.SPXsigma

    def __init__(self, ticker='SPY', init_value=1, mu=DEFAULT_MU,
                 sigma=DEFAULT_SIGMA, date_range=DEFAULT_DATE_RANGE):
        super().__init__(
            asset_type='Equity',
            initial_balance=init_value,
            date_range = date_range
            )
        self.ticker=ticker
        self.init_value = init_value
        self.mu = mu
        self.sigma = sigma


    def _generate_returns(self):
        return fe_sim.gmix2ret(N=len(self.date_range), mean=self.mu, sigma=self.sigma)


    def _get_compound_factors(self, date_diffs):
        return (pd.Series(
                    index=self.date_range,
                    data=self._generate_returns()
                    ).shift(1)
                .reindex(date_diffs.index)
                .resample('D')
                .first()
                .fillna(1.0)
                )


    def _generate_price_path(self, label=None):
        # Unclear that we need this plus simulate_path
        return self.value_through_time


    def simulate_path(self):
        # Unclear that we need this plus _generate_price_path or the resample.pad()
        return self._generate_price_path().resample('D').pad()


    def _generate_price_paths(self, how_many, write_type=None):
        """
            write_type: str, default None
                None - don't save paths to object
                overwrite - overwrite whatever's in self._price_paths
                append - add to whatever's in self._price_paths
                error - raise ValueError when self._price_paths is not empty else write to it
        """
        paths = []
        for x in range(how_many):
            paths.append(self._generate_price_path())

        # TO DO: This is probably unacceptably gross, so we should rewrite it
        if write_type is None:
            pass
        elif write_type == 'overwrite':
            self._price_paths = paths
        elif write_type == 'append':
            if hasattr(self, '_price_paths'):
                self._price_paths.append(paths)
            else:
                self._price_paths = paths
        elif write_type == 'error':
            if hasattr(self, '_price_paths'):
                raise ValueError("self._price_paths is not empty, if you want to overwrite or append, specify w/ write_type")
            else:
                self._price_paths = paths
        else:
            raise ValueError(f"{write_type} is not an acceptable value for write_type")

        return paths


    def plot_price_paths(self, max_plots=1, random_sample=True, **kwargs):
        all_paths = (self._price_paths if hasattr(self, '_price_paths')
                     else self._generate_price_paths(how_many=max_plots)
                     )
        paths_to_plt = (random.sample(all_paths, max_plots) if random_sample
                        else all_paths[:max_plots]
                        )
        return pd.concat(paths_to_plt, axis=1).plot(**kwargs)


    def plot_price_path_quantiles(self, min_n=200, quantiles=[0.25, 0.5, 0.75],
                                  return_df=False, show_mean=False, **kwargs):
        n_paths_to_gen = (min_n if not hasattr(self, '_price_paths')
                          else min_n - len(self._price_paths)
                          )
        new_paths = self._generate_price_paths(how_many=n_paths_to_gen)
        all_paths = (self._price_path.append(new_paths) if hasattr(self, '_price_paths')
                     else new_paths
                     )
        all_paths_df = pd.concat(all_paths, axis=1)
        quantiles = all_paths_df.quantile(q=quantiles, axis=1).T
        if show_mean: quantiles['mean'] = all_paths_df.mean(axis=1)
        quantiles.plot(**kwargs)
        if return_df: return quantiles


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
            { k: v.simulate_path() for k,v in self.contents.items() }
        ).fillna(method='bfill')

        df['total'] = df.sum(axis=1)

        return df

    def generate_value_path(self):
        return self.generate_path_df()['total']

    @property
    def current_value(self):
        today = pd.datetime.today().date()
        return self.generate_value_path()[today:].iloc[0]
