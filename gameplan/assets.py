import numpy as np
import pandas as pd
import random

import fecon236.prob.sim as fe_sim

from gameplan.cashflows import CashFlow
from gameplan.collections import Contributions
from gameplan.contributions import Contribution


class Asset():
    def __init__(self, asset_type):
        self.asset_type = asset_type

    def simulate_path(self, **kwargs):
        raise NotImplementedError


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
        self.date_range = date_range


    def add_contribution(self, contribution, label=None, if_exists='error'):
        label = label if label else contribution.name
        self.contributions.add_object(contribution, label, if_exists)


    @property
    def value_through_time(self):
        t = (
            self.contributions.total
            .reindex(index=self.date_range, fill_value=0)
            .resample('D').sum() # downsample to daily)
        ) # get a daily view of contributions over the entire self.date_range
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
        self.ticker=ticker
        self.init_value = init_value
        self.mu = mu
        self.sigma = sigma
        self.date_range = date_range


    def _generate_returns(self):
        return fe_sim.gmix2ret(N=len(self.date_range), mean=self.mu, sigma=self.sigma)


    def _generate_price_path(self, label=None):
        returns = self._generate_returns()
        prices = self.init_value * pd.Series(
            index=self.date_range,
            data=returns,
            name=label
        ).cumprod()

        return prices


    def simulate_path(self):
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
