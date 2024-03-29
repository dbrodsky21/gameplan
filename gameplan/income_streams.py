from datetime import datetime
import pandas as pd
import numpy as np
from typing import Callable, List, Optional, Union, Tuple

from gameplan.cashflows import CashFlow
from gameplan.gp_collections import CashFlowCollection
from gameplan.contributions import Deduction
from gameplan.growth.growth_series import GrowthSeries, FittedPolynomialGrowth
import gameplan.helpers as hp


class IncomeStream(CashFlow):
    def __init__(self, income_type, amount=None, freq=None, start_dt=None,
                 end_dt=None, date_range=None, values=None, tax_rate=0.0,
                 growth_series=None, growth_per_period_fn=None,
                 growth_freq=pd.DateOffset(years=1), min_growth=None,
                 max_growth=None, growth_start_dt=None, growth_end_dt=None,
                 incorporate_growth=True, incorporate_discounting=True,
                 yearly_discount_rate=0.02, **kwargs):
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
            growth_series = growth_series,
            growth_start_dt=growth_start_dt,
            growth_end_dt=growth_end_dt,
            growth_freq=growth_freq,
            min_growth=min_growth,
            max_growth=max_growth,
            growth_per_period_fn=growth_per_period_fn,
            incorporate_growth=incorporate_growth,
            incorporate_discounting=incorporate_discounting,
            yearly_discount_rate=yearly_discount_rate,
            **kwargs
        )
        self.tax_rate = tax_rate


class Salary(IncomeStream):
    def __init__(self,
                 paycheck_amt: float,
                 payday_freq: Optional[pd.DateOffset] = None,
                 next_paycheck_dt: Optional[pd.datetime] = None,
                 last_paycheck_dt: Optional[pd.datetime] = None,
                 tax_rate: float = 0.0,
                 growth_series: GrowthSeries = FittedPolynomialGrowth,
                 growth_points_to_fit: List[Tuple[int, float]] = [(0, 1.0),],
                 growth_freq: Union[str, datetime] = pd.DateOffset(years=1),
                 min_growth: Optional[float] = None,
                 max_growth: Optional[float] = None,
                 growth_start_dt: Optional[Union[str, datetime]] = None,
                 growth_end_dt: Optional[Union[str, datetime]] = None,
                 incorporate_growth: bool = True,
                 incorporate_discounting: bool = False,
                 yearly_discount_rate: float = 0.0,
                 **kwargs) -> None:

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
            growth_series=growth_series,
            growth_freq=growth_freq,
            min_growth=min_growth,
            max_growth=max_growth,
            growth_start_dt=growth_start_dt,
            growth_end_dt=growth_end_dt,
            addtl_growth_params=dict(points_to_fit=growth_points_to_fit),
            incorporate_growth=incorporate_growth,
            incorporate_discounting=incorporate_discounting,
            yearly_discount_rate=yearly_discount_rate,
            **kwargs
        )
        self.deductions = CashFlowCollection(
            objects={},
            totals_col_label='total_deductions'
            )

    def _create_deduction(self, label, amt=None, pct=None, max_amt=None,
                          max_amt_freq=None):
        """
        Note that there's a time component here as well, where amt/pct should
        maybe be a timeseries.
        """
        if all([amt, pct]) or not any([amt, pct]):
            # Note that (pct or amt == 0 will read as a False)
            raise ValueError("Exactly one of [amt, pct] must not be None")
        if amt:
            deduction = Deduction(
                deduction_label=label,
                date_range=self.date_range,
                values=[amt] * len(self.date_range),
            )
        elif pct:
            deduction = Deduction.from_income_stream(
                income_stream=self,
                pct=pct,
                label=label,
                max_amt=max_amt,
                max_amt_freq=max_amt_freq,
                )
        else:
            pass

        return deduction

    def add_deduction(self, deduction=None, label=None, amt=None, pct=None,
                      max_amt=None, max_amt_freq=None, if_exists='error'):

        if not deduction:
            deduction = self._create_deduction(label, amt, pct, max_amt,
                                               max_amt_freq)

        label = label if label else deduction.name
        self.deductions.add_object(deduction, label, if_exists)

    @property
    def salary_df(self):
        return super().cash_flows_df

    @property
    def total_deductions(self):
        vals = (self.deductions.total if not pd.Series(self.deductions.total).empty
                else self.salary_df['salary'] * 0.0) # create a 0-filled series if no deductions
        return pd.Series(vals, name='total_deductions')

    @property
    def post_deductions(self):
        # deductions are a negative value
        post_deductions = self.salary_df['salary'] + self.total_deductions
        return pd.Series(post_deductions, name='salary_post_deductions')

    @property
    def total_taxes(self):
        total_taxes = -1 * self.post_deductions * self.tax_rate
        return pd.Series(total_taxes, name='total_taxes')

    @property
    def take_home_salary(self):
        post_taxes = self.post_deductions + self.total_taxes
        return pd.Series(post_taxes, name='take_home_salary')

    @property
    def cash_flows_df(self):
        df = pd.concat([
                self.salary_df['salary'],
                self.deductions.as_df.drop(columns=['total_deductions']),
                self.total_taxes, # taxes should be a negative cashflow
            ], axis=1)
        return df

    @property
    def annualized_salary(self):
        """TO DO: refactor"""
        return self.salary_df.resample('365D').sum().values[0][0]


class IncomeStreams(CashFlowCollection):
    def __init__(self, income_streams={}):
        super().__init__(collection_type=IncomeStream, objects=income_streams)
