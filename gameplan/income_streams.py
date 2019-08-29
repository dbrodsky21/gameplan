import pandas as pd
import numpy as np

from gameplan.cashflows import CashFlow
from gameplan.collections import CashFlowCollection
from gameplan.contributions import Deduction
import gameplan.helpers as hp


class IncomeStream(CashFlow):
    def __init__(self, income_type, amount=None, freq=None, start_dt=None,
                 end_dt=None, date_range=None, values=None, tax_rate=0.0,
                 growth_freq=pd.DateOffset(years=1), min_growth=0.0,
                 max_growth=0.0, growth_start_dt=None, growth_end_dt=None):
        super().__init__(
            cashflow_type='income',
            name=income_type,
            amount=amount,
            freq=freq,
            start_dt=start_dt,
            end_dt=end_dt,
            date_range=date_range,
            values=values,
            recurring=True,
            outflow=False,
            growth_freq=growth_freq,
            min_growth=min_growth,
            max_growth=max_growth,
            growth_start_dt=growth_start_dt,
            growth_end_dt=growth_end_dt

        )
        self.tax_rate = tax_rate


class Salary(IncomeStream):
    def __init__(self, paycheck_amt, payday_freq, next_paycheck_dt=None,
                 last_paycheck_dt=None, tax_rate=0.0,
                 growth_freq=pd.DateOffset(years=1), min_growth=0.0,
                 max_growth=0.0, growth_start_dt=None, growth_end_dt=None):

        start_dt = (
            next_paycheck_dt if next_paycheck_dt
            else hp.get_offset_date(payday_freq)
        )
        # TO DO: add validation that first/last dts aren't conflicting
        end_dt = (
            last_paycheck_dt if last_paycheck_dt
            else start_dt + pd.DateOffset(years=20)
        )
        super().__init__(
            income_type='salary',
            amount=paycheck_amt,
            freq=payday_freq,
            start_dt=start_dt,
            end_dt=end_dt,
            tax_rate=tax_rate,
            growth_freq=growth_freq,
            min_growth=min_growth,
            max_growth=max_growth,
            growth_start_dt=growth_start_dt,
            growth_end_dt=growth_end_dt
        )
        self.deductions = CashFlowCollection(
            objects={},
            totals_col_label='total_deductions'
            )



    def _create_deduction(self, label, amt=None, pct=None):
        """
        Note that there's a time component here as well, where amt/pct should
        maybe be a timeseries.
        """
        if all([amt, pct]) or not any([amt, pct]):
            # Note that (pct or amt == 0 will read as a False)
            raise ValueError("Exactly one of [amt, pct] must not be None")
        contrib_amt = amt if amt else self.amount * pct
        deduction = Deduction(
            deduction_label=label,
            date_range=self.date_range,
            values=[contrib_amt] * len(self.date_range),
        )

        return deduction


    def add_deduction(self, deduction=None, label=None, amt=None, pct=None,
                      if_exists='error'):

        if not deduction:
            deduction = self._create_deduction(label, amt, pct)

        label = label if label else deduction.name
        self.deductions.add_object(deduction, label, if_exists)

    @property
    def total_deductions(self):
        vals = (self.deductions.total if not pd.Series(self.deductions.total).empty
                else self.cash_flows_df['salary'] * 0.0) # create a 0-filled series if no deductions
        return pd.Series(vals, name='total_deductions')


    @property
    def post_deductions(self):
        # deductions are a negative value
        post_deductions = self.cash_flows_df['salary'] + self.total_deductions
        return pd.Series(post_deductions, name='salary_post_deductions')

    @property
    def total_taxes(self):
        total_taxes = self.post_deductions * self.tax_rate
        return pd.Series(total_taxes, name='total_taxes')


    @property
    def take_home_salary(self):
        post_taxes = self.post_deductions - self.total_taxes
        return pd.Series(post_taxes, name='take_home_salary')

    @property
    def paycheck_df(self):
        df = pd.concat([
                self.cash_flows_df['salary'],
                self.total_deductions,
                -self.total_taxes, # taxes should be a negative cashflow
                self.take_home_salary
            ], axis=1)
        return df

    @property
    def annualized_salary(self):
        """TO DO: refactor"""
        return self.cash_flows_df.resample('365D').sum().values[0][0]


    @property
    def _growth_fn(self):
        # Placeholder; will want better logic around distributions
        grwth = lambda x: 1 + np.random.uniform(low=self.min_growth,
                                                high=self.max_growth)
        return grwth


    def get_growth_path(self, return_df=False, start_dt=None, end_dt=None,
                        growth_freq=None, growth_fn=None):
        return super().get_growth_path(
            return_df=return_df,
            start_dt=start_dt if start_dt else self.growth_start_dt,
            end_dt=end_dt if end_dt else self.growth_end_dt,
            growth_freq=growth_freq if growth_freq else self.growth_freq,
            growth_fn=growth_fn if growth_fn else self._growth_fn
        )

    def update_values_with_growth(self, start_dt=None, end_dt=None,
                                  growth_freq=None, growth_fn=None):
        super().update_values_with_growth(
            start_dt=start_dt if start_dt else self.growth_start_dt,
            end_dt=end_dt if end_dt else self.growth_end_dt,
            growth_freq=growth_freq if growth_freq else self.growth_freq,
            growth_fn=growth_fn if growth_fn else self._growth_fn
        )





    # #generic
    # def update_values_with_growth(self, **kwargs):
    #     initial_series = pd.Series(self._initial_values, index=self.date_range)
    #     growth_series = self.get_growth_series(**kwargs)
    #     updated_values = initial_series.multiply(growth_series, axis=0)
    #     self._values = updated_values


    # @staticmethod
    # def get_growth_factor(lower=-1, upper=1, dist=np.random.uniform):
    #     # Placeholder; will want better logic around distributions
    #     return dist(lower, upper)
    #
    #
    # def get_growth_series(self, start_dt=None, update_freq_weeks=52,
    #                       growth_factor_range=(-1.0, 1.0)):
    #     index = (
    #         self.cash_flows_df
    #         [start_dt:]
    #         .asfreq(pd.offsets.Week(n=update_freq_weeks))
    #         .index
    #     )
    #     growth = (
    #         pd.Series(index=index)
    #         .apply(
    #             lambda x: 1 + Salary.get_growth_factor(*growth_factor_range)
    #         )
    #     )
    #     growth_series = (
    #         growth
    #         .reindex_like(self.cash_flows_df)
    #         .fillna(1)
    #         .cumprod()
    #     )
    #     return growth_series
    #
    #

class IncomeStreams(CashFlowCollection):
    def __init__(self, income_streams={}):
        super().__init__(collection_type=IncomeStream, objects=income_streams)
