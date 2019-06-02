import pandas as pd
import numpy as np

FREQ_MAP = {
    'Y': pd.DateOffset(years=1),
}
class IncomeStream():
    def __init__(self, income_type, amount, freq='Y',
                 first_pmt_dt=pd.datetime.today(),
                 last_pmt_dt=pd.datetime.today() + pd.DateOffset(years=5)):
        self.income_type = income_type
        self.amount = amount
        self.freq = freq
        self.first_pmt_dt = first_pmt_dt
        self.last_pmt_dt = last_pmt_dt

    @property
    def cash_flows(self):
        """A pandas dataframe representing the cashflows from the income stream.
        """
        freq = FREQ_MAP.get(self.freq, self.freq)
        date_range = pd.date_range(
            start=self.first_pmt_dt,
            end=self.last_pmt_dt,
            freq=freq,
            normalize=True
        )

        cash_flows = pd.DataFrame(
            index=date_range,
            data=[self.amount] * len(date_range),
            columns=[self.income_type]
        )

        return cash_flows


    def plot_cash_flows(self, cumulative=True, **kwargs):
        if cumulative:
            to_plt = (
                self.cash_flows
                .resample('d')
                .mean()
                .cumsum()
                .fillna(method='ffill')
            )
            chart_type = 'line'
        else:
            to_plt = self.cash_flows
            chart_type = 'bar'

        to_plt.plot(kind=chart_type, **kwargs)

# Do you expect it to (and not be replaced by a similar income stream) anytime soon? If so, when?


# class Salary(IncomeStream):
#     def annualize_salary(self, salary, fmt):
#         if fmt.lower() == 'year':
#             salary_annualized = salary
#         elif fmt.lower() == 'month':
#             salary_annualized = 12 * salary
#         elif fmt.lower() == 'week':
#             salary_annualized = 52 * salary
#         else:
#             raise ValueError("fmt.lower() must be one of ['year', 'month', 'week']")
#
#         return salary_annualized
#
#     def __init__(self, salary, sal_fmt, sal_freq , next_paycheck_dt, years=1, tax_withholding_rate=0.35):
#         super().__init__(income_type='salary')
#
#
#         self.salary_annualized = self.annualize_salary(float(salary), sal_fmt)
#         self.FREQ_MAP = {
#             'weekly': dict(periods=52, freq='7D'),
#             'bi-weekly': dict(periods=26, freq='14D'),
#             'twice monthly': dict(periods=24, freq='SM'), # [1st and 15th ('SMS') or 15th and last day of month ('SM)]
#             'monthly': dict(periods=12, freq=pd.DateOffset(months=1, day=next_paycheck_dt.day))
#         }
#         self.payday_freq = sal_freq
#         self._annual_pmt_periods = self.FREQ_MAP.get(sal_freq).get('periods')
#         self._pmt_freqs = self.FREQ_MAP.get(sal_freq).get('freq')
#         self._pmt_size = self.salary_annualized/self._annual_pmt_periods
#
#         self.date_range = pd.date_range(
#             start=next_paycheck_dt,
#             periods=(years * self._annual_pmt_periods),
#             freq=self._pmt_freqs
#         )
#
#         self.tax_withholding_rate = tax_withholding_rate
#
#
#     @property
#     def cash_flow(self):
#         pmt = self._pmt_size * (1 - self.tax_withholding_rate)
#         ## TO DO: consider adding other witholding stuff
#         return pmt
#
#
#     @property
#     def cash_flows(self):
#         pmt = self.cash_flow
#         df = pd.DataFrame(
#             index=self.date_range,
#             data=[pmt]*len(self.date_range),
#             columns=['salary']
#         )
#         # Consider adding columns for [salary, after-tax, after withholding, etc.]
#
#         return df
#
#
#     def plot_salary_pmts(self, **kwargs):
#         self.cash_flows.resample('d').mean().cumsum().fillna(method='ffill').plot(**kwargs)
