import numpy as np
import pandas as pd

from gameplan.growth.data_sources import KitcesData


class KitcesIncomeGrowthModel():
    def __init__(self,
                 user_birthday: pd.datetime,
                 data_source: KitcesData = KitcesData(),
                 income_percentile: int = 50,
                 degree_poly_to_fit: int = 3,
                ) -> None:
        self.user_birthday = user_birthday
        self.data_source = data_source
        self._income_percentile = income_percentile
        self.growth_series = self._get_relevant_series()
        self._degree_poly_to_fit = degree_poly_to_fit
        self.fitted_polynomial = self._fit_polynomial(
            poly_degree=self._degree_poly_to_fit
            )

    def get_growth_points_to_fit(self,
                                 start_dt: pd.datetime = pd.datetime.today(),
                                 ) -> pd.Series:
        age_at_ref_date = (start_dt - self.user_birthday).days
        growth_level_at_ref_date = self.fitted_polynomial(age_at_ref_date)
        new_growth_series = self.growth_series.loc[age_at_ref_date:]
        new_growth_series.loc[age_at_ref_date] = growth_level_at_ref_date
        new_growth_series = new_growth_series.divide(growth_level_at_ref_date)
        new_growth_series.index = new_growth_series.index - age_at_ref_date

        return new_growth_series.sort_index()

    @property
    def income_percentile(self) -> int:
        return self._income_percentile

    @income_percentile.setter
    def income_percentile(self, val: int) -> None:
        valid_vals = self.data_source.cleaned_data.columns
        if val not in valid_vals:
            raise ValueError(f"income_percentile must be one of: {valid_vals}")
        self._income_percentile = val
        self.growth_series = self._get_relevant_series()
        self.fitted_polynomial = self._fit_polynomial(
            poly_degree=self._degree_poly_to_fit
            )

    def _get_relevant_series(self) -> pd.Series:
        relevant_col = self.income_percentile
        return self.data_source.cleaned_data.loc[:, relevant_col]

    def _fit_polynomial(self,
                        poly_degree: int = 3
                        ) -> np.polynomial.polynomial.Polynomial:
        xs = self.growth_series.index
        ys= self.growth_series.values
        fitted_poly = np.polynomial.polynomial.Polynomial.fit(xs, ys, deg=poly_degree)
        return fitted_poly
