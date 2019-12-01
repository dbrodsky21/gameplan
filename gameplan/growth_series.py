import numpy as np
import pandas as pd
import scipy
from typing import Optional, List
import warnings

import gameplan.helpers as hp
from gameplan.growth_funcs import exponential_fn, linear_fn, logistic_fn

class GrowthSeries():
    DEFAULT_END_DT_OFFSET = pd.DateOffset(years=20)

    def __init__(self, date_range=None, start_dt=None, end_dt=None,
                 freq=pd.DateOffset(years=1),
                 growth_per_period_fn=None,
                 min_val=0,
                 max_val=None,
                 **kwargs):

        if date_range is not None:
            self.start_dt = date_range.min()
            self.end_dt = date_range.max()
            self.freq = date_range.freq
        else:
            self.start_dt = start_dt
            self.end_dt = (end_dt if end_dt
                           else start_dt + self.DEFAULT_END_DT_OFFSET)
            self.freq=freq

        self.growth_per_period_fn = growth_per_period_fn or (lambda x: 0)
        self.min_val = min_val
        self.max_val = max_val


    @property
    def date_range(self):
        freq = hp.FREQ_MAP.get(self.freq, self.freq)
        date_range = pd.date_range(
            start=self.start_dt,
            end=self.end_dt,
            freq=freq,
            normalize=True
        )
        return date_range


    @property
    def days_from_start(self):
        """
        Get self.date_range expressed as days from start_dt.
        TO DO: Think about exposing period_resolution == '1D'
        """
        n_periods = [(x - self.date_range.min())/pd.Timedelta('1D')
                     for x in self.date_range]
        return n_periods


    @property
    def growth_per_period(self):
        vals = [ 1 + self.growth_per_period_fn(x) for x in self.days_from_start]
        return pd.Series(vals)

    @property
    def growth_series(self):
        cum_vals = self.growth_per_period.cumprod().fillna(1).values
        cum_vals_series = pd.Series(cum_vals, index=self.date_range)

        return cum_vals_series.clip(lower=self.min_val, upper=self.max_val)


class StochasticGrowth(GrowthSeries):
    def __init__(self, date_range=None, start_dt=None, end_dt=None,
                 freq=pd.DateOffset(years=1),
                 growth_per_period_fn=lambda x: np.random.uniform(0.01, 0.05),
                 min_val=0, max_val=None, **kwargs):
        super().__init__(
            date_range=date_range,
            start_dt=start_dt,
            end_dt=end_dt,
            freq=freq,
            growth_per_period_fn=growth_per_period_fn,
            min_val=min_val,
            max_val=max_val
        )


class FittedPolynomialGrowth(GrowthSeries):
    def __init__(self, degree=3, date_range=None, start_dt=None, end_dt=None,
                 freq=pd.DateOffset(years=1),
                 # parameter_bounds=None,
                 points_to_fit=[(0, 1)],
                 # initial_param_guesses=None,
                 min_val=None,
                 max_val=None,
                 **kwargs
                ):
        super().__init__(
            date_range=date_range,
            start_dt=start_dt,
            end_dt=end_dt,
            freq=freq,
            min_val=min_val,
            max_val=max_val
        )
        self.degree = degree
        # self.growth_param_bounds = parameter_bounds
        self.points_to_fit = points_to_fit
        # self.initial_param_guesses = initial_param_guesses


    def add_points_to_fit(self, points: [(float, float)], return_pts=False):
        self.points_to_fit = np.unique(self.points_to_fit + points, axis=0)
        if return_pts:
            return self.points_to_fit


    @property
    def _fitted_polynomial(self):
        xs = [n[0] for n in self.points_to_fit]
        ys = [n[1] for n in self.points_to_fit]
        # see domain param for below if fitting poorly out of sample.
        poly = np.polynomial.polynomial.Polynomial.fit(xs, ys, deg=self.degree)

        return poly


    @property
    def growth_per_period(self):
        cum_vals = [self._fitted_polynomial(x) for x in self.days_from_start]
        vals = 1 + pd.Series(cum_vals).pct_change()
        return vals


class FittedGrowthSeries(GrowthSeries):
    def __init__(self, growth_fn, date_range=None, start_dt=None, end_dt=None,
                 freq=pd.DateOffset(years=1),
                 parameter_bounds=None,
                 points_to_fit=[(0, 1)],
                 initial_param_guesses=None,
                 min_val=None,
                 max_val=None,
                 **kwargs
                ):
        super().__init__(
            date_range=date_range,
            start_dt=start_dt,
            end_dt=end_dt,
            freq=freq,
            min_val=min_val,
            max_val=max_val
        )
        self.growth_fn = growth_fn
        self.growth_param_bounds = parameter_bounds
        self.points_to_fit = points_to_fit
        self.initial_param_guesses = initial_param_guesses


    def add_points_to_fit(self, points: [(float, float)], return_pts=False):
        self.points_to_fit = np.unique(self.points_to_fit + points, axis=0)
        if return_pts:
            return self.points_to_fit


    @property
    def _fitted_growth_params(self):
        xs = [n[0] for n in self.points_to_fit]
        ys = [n[1] for n in self.points_to_fit]
        fitted_params, _ = scipy.optimize.curve_fit(
            f=self.growth_fn,
            xdata=xs,
            ydata=ys,
            bounds=self.growth_param_bounds,
            p0=self.initial_param_guesses
        )

        return fitted_params


    @property
    def growth_per_period(self):
        cum_vals = [self.growth_fn(x, *self._fitted_growth_params)
                    for x in self.days_from_start]
        vals = 1 + pd.Series(cum_vals).pct_change()
        return vals


class LogisticGrowth(FittedGrowthSeries):
    def __init__(self, date_range=None, start_dt=None, end_dt=None,
                 freq=pd.DateOffset(years=1),
                 growth_fn=logistic_fn,
                 parameter_bounds=([0, 0, 0],  np.inf),
                 points_to_fit=[(0, 1)],
                 min_val=None,
                 max_val=None,
                 **kwargs
                ):
        super().__init__(
            date_range=date_range,
            start_dt=start_dt,
            end_dt=end_dt,
            freq=freq,
            min_val=min_val,
            max_val=max_val,
            growth_fn=growth_fn,
            parameter_bounds=parameter_bounds,
            points_to_fit=points_to_fit
        )


    @property
    def initial_param_guesses(self):
        return self.__initial_param_guesses


    @initial_param_guesses.setter
    def initial_param_guesses(self, params: Optional[List[float]]) -> None:
        max_y_pt = max([y for x, y in self.points_to_fit])
        max_y = self.max_val or max_y_pt
        if params is not None:
            params[0] = max(max_y, params[0])
        else:
            params = [max_y, 0, 0]
        self.__initial_param_guesses = params


class LinearGrowth(FittedGrowthSeries):
    def __init__(self, date_range=None, start_dt=None, end_dt=None,
                 freq=pd.DateOffset(years=1),
                 growth_fn=linear_fn,
                 parameter_bounds=([0, 0],  np.inf),
                 points_to_fit=[(0, 1)],
                 initial_param_guesses=(0, 0),
                 min_val=None,
                 max_val=None,
                 **kwargs
                ):
        super().__init__(
            date_range=date_range,
            start_dt=start_dt,
            end_dt=end_dt,
            freq=freq,
            growth_fn=growth_fn,
            parameter_bounds=parameter_bounds,
            points_to_fit=points_to_fit,
            initial_param_guesses=initial_param_guesses,
            min_val=min_val,
            max_val=max_val
        )


class ExponentialGrowth(FittedGrowthSeries):
    def __init__(self, date_range=None, start_dt=None, end_dt=None,
                 freq=pd.DateOffset(years=1),
                 growth_fn=exponential_fn,
                 parameter_bounds=([0, 0],  np.inf),
                 points_to_fit=[(0, 1)],
                 initial_param_guesses=(1, 0),
                 min_val=None,
                 max_val=None,
                 **kwargs
                ):
        super().__init__(
            date_range=date_range,
            start_dt=start_dt,
            end_dt=end_dt,
            freq=freq,
            growth_fn=growth_fn,
            parameter_bounds=parameter_bounds,
            points_to_fit=points_to_fit,
            initial_param_guesses=initial_param_guesses,
            min_val=min_val,
            max_val=max_val
        )