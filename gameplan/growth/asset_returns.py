import pandas as pd
from typing import Dict, List

import fecon236.prob.sim as fe_sim


class AssetReturns():
    def __init__(self):
        self.equity = {}
        self.fixed_income = {}
        self.cash_savings = {}


    def add_ticker(self, asset_type, ticker):
        asset_class = getattr(self, asset_type)
        if asset_class.get(ticker):
            warnings.warn(f"{ticker} already populated, not overwriting")
        else:
            if asset_type == 'equity':
                # I'm not passing mu & sigma here, not sure if that's right
                asset_class[ticker] = EquityReturnsSeries(symbol=ticker)
            else:
                raise NotImplementedError(f"Haven't implemented subclass for {asset_type}")

        return asset_class[ticker]

    def get_returns_series(self, asset_type, ticker):
        asset_class = getattr(self, asset_type, None)
        series = asset_class.get(ticker) or self.add_ticker(asset_type, ticker)
        return series


class EquityReturnsSeries():
    DEFAULT_MU = fe_sim.SPXmean
    DEFAULT_SIGMA = fe_sim.SPXsigma
    DEFAULT_DATE_RANGE = pd.date_range(
        start=pd.datetime.today().date(),
        end=pd.datetime(2100, 1, 1),
        freq='B'
    )

    def __init__(self, symbol, date_range=DEFAULT_DATE_RANGE, mu=DEFAULT_MU, sigma=DEFAULT_SIGMA):
        self.symbol = symbol
        self.date_range = date_range
        self.mu = mu
        self.sigma = sigma
        self.returns_df = pd.DataFrame(index=date_range)
        self.add_series_to_returns_df()

    def _get_model_params(self) -> Dict[str, float]:
        # TO DO: make ticker specific, e.g. mu, sigma = lookup_mu_sigma(ticker=self.symbol)
        model_params = dict(
            n_obs=len(self.date_range),
            mu=self.mu,
            sigma=self.sigma
            )
        self.model_params = model_params
        return model_params

    def model(self, n_obs, mu, sigma) -> List[float]:
        return fe_sim.gmix2ret(N=n_obs, mean=mu, sigma=sigma)

    def generate_returns(self) -> List[float]:
        model_params = getattr(self, 'model_params', self._get_model_params())
        return self.model(**model_params)

    def add_series_to_returns_df(self):
        n_existing_series = len(self.returns_df.columns)
        new_series_name = f'sim_{n_existing_series + 1}'
        self.returns_df[new_series_name] = self.generate_returns()



# def _generate_price_path(self, label=None):
#       # Unclear that we need this plus simulate_path
#       return self.value_through_time
#
#
#   def simulate_path(self):
#       # Unclear that we need this plus _generate_price_path or the resample.pad()
#       return self._generate_price_path().resample('D').pad()
#
#
#   def _generate_price_paths(self, how_many, write_type=None):
#       """
#           write_type: str, default None
#               None - don't save paths to object
#               overwrite - overwrite whatever's in self._price_paths
#               append - add to whatever's in self._price_paths
#               error - raise ValueError when self._price_paths is not empty else write to it
#       """
#       paths = []
#       for x in range(how_many):
#           paths.append(self._generate_price_path())
#
#       # TO DO: This is probably unacceptably gross, so we should rewrite it
#       if write_type is None:
#           pass
#       elif write_type == 'overwrite':
#           self._price_paths = paths
#       elif write_type == 'append':
#           if hasattr(self, '_price_paths'):
#               self._price_paths.append(paths)
#           else:
#               self._price_paths = paths
#       elif write_type == 'error':
#           if hasattr(self, '_price_paths'):
#               raise ValueError("self._price_paths is not empty, if you want to overwrite or append, specify w/ write_type")
#           else:
#               self._price_paths = paths
#       else:
#           raise ValueError(f"{write_type} is not an acceptable value for write_type")
#
#       return paths
#
#
#   def plot_price_paths(self, max_plots=1, random_sample=True, **kwargs):
#       all_paths = (self._price_paths if hasattr(self, '_price_paths')
#                    else self._generate_price_paths(how_many=max_plots)
#                    )
#       paths_to_plt = (random.sample(all_paths, max_plots) if random_sample
#                       else all_paths[:max_plots]
#                       )
#       return pd.concat(paths_to_plt, axis=1).plot(**kwargs)
#
#
#   def plot_price_path_quantiles(self, min_n=200, quantiles=[0.25, 0.5, 0.75],
#                                 return_df=False, show_mean=False, **kwargs):
#       n_paths_to_gen = (min_n if not hasattr(self, '_price_paths')
#                         else min_n - len(self._price_paths)
#                         )
#       new_paths = self._generate_price_paths(how_many=n_paths_to_gen)
#       all_paths = (self._price_path.append(new_paths) if hasattr(self, '_price_paths')
#                    else new_paths
#                    )
#       all_paths_df = pd.concat(all_paths, axis=1)
#       quantiles = all_paths_df.quantile(q=quantiles, axis=1).T
#       if show_mean: quantiles['mean'] = all_paths_df.mean(axis=1)
#       quantiles.plot(**kwargs)
#       if return_df: return quantiles
