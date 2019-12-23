import pandas as pd
import numpy as np

class Liability():
    def __init__(liability_type):
        self.liability_type = liability_type

class Asset():
    def __init__(asset_type):
        self.asset_type = asset_type



class CashFlow():
    pass

class Expense():
    FREQ_CONFIG = {
        'M': dict(
            start=pd.datetime.today() + pd.offsets.MonthBegin(normalize=True),
            periods=12,
            freq='MS'
        )
    }

    def __init__(self, exp_type, amount, freq):
        self.exp_type = exp_type
        self.amount = amount
        self.freq = freq
        self._freq_config = self.FREQ_CONFIG.get(self.freq)
        self._date_range = pd.date_range(
            start=self._freq_config['start'],
            periods=self._freq_config['periods'],
            freq=self._freq_config['freq'],
        )


    @property
    def cash_flows(self):
        df =  pd.DataFrame(
            index=self._date_range,
            data=[self.amount]*len(self._date_range),
            columns=[self.exp_type]
        )

        return df


class Rent(Expense):
    def __init__(self, amount, freq='M'):
        """TO DO: include a date_of_pmt thing?"""
        super().__init__(exp_type='rent', amount=amount, freq=freq)


class Utilities(Expense):
    def __init__(self, amount, freq='M'):
        super().__init__(exp_type='utilities', amount=amount, freq=freq)

class Stock(): # should be type Investment
    def __init__(self, ticker, shares=None, share_price=None, expected_growth=None, vol=None):
        self.ticker=ticker
        self.shares=shares
        self.share_price = share_price if share_price else self.get_share_price(ticker)
        self.expected_growth = expected_growth if expected_growth else self.get_expected_growth(ticker)
        self.vol = vol if vol else self.get_vol(ticker)

    def get_share_price(self, ticker):
        ## TO DO
        return None

    def get_expected_growth(self, ticker):
        ## TO DO
        return None

    def get_vol(self, ticker):
        ## TO DO
        return None

    def simulate_path(self, periods):
        daily_growth = self.expected_growth/365
        daily_vol = self.vol/365
        daily_returns = 1 + np.random.normal(daily_growth, daily_vol, periods)
        price_path = self.share_price * np.cumprod(daily_returns)

        return price_path

    def get_price_paths(self, n_paths, periods=365):
        if not hasattr(self, '_price_paths'):
            self._price_paths = []
        for x in range(n_paths):
            self._price_paths.append(self.simulate_path(periods=periods))

class Salary():
    def annualize_salary(self, salary, fmt):
        if fmt.lower() == 'year':
            salary_annualized = salary
        elif fmt.lower() == 'month':
            salary_annualized = 12 * salary
        elif fmt.lower() == 'week':
            salary_annualized = 52 * salary
        else:
            raise ValueError("fmt.lower() must be one of ['year', 'month', 'week']")

        return salary_annualized

    def __init__(self, salary, sal_fmt, sal_freq , next_paycheck_dt, years=1, tax_withholding_rate=0.35):
        self.salary_annualized = self.annualize_salary(float(salary), sal_fmt)
        self.FREQ_MAP = {
            'weekly': dict(periods=52, freq='7D'),
            'bi-weekly': dict(periods=26, freq='14D'),
            'twice monthly': dict(periods=24, freq='SM'), # [1st and 15th ('SMS') or 15th and last day of month ('SM)]
            'monthly': dict(periods=12, freq=pd.DateOffset(months=1, day=next_paycheck_dt.day))
        }
        self.payday_freq = sal_freq
        self._annual_pmt_periods = self.FREQ_MAP.get(sal_freq).get('periods')
        self._pmt_freqs = self.FREQ_MAP.get(sal_freq).get('freq')
        self._pmt_size = self.salary_annualized/self._annual_pmt_periods

        self.date_range = pd.date_range(
            start=next_paycheck_dt,
            periods=(years * self._annual_pmt_periods),
            freq=self._pmt_freqs
        )

        self.tax_withholding_rate = tax_withholding_rate


    @property
    def cash_flow(self):
        pmt = self._pmt_size * (1 - self.tax_withholding_rate)
        ## TO DO: consider adding other witholding stuff
        return pmt


    @property
    def cash_flows(self):
        pmt = self.cash_flow
        df = pd.DataFrame(
            index=self.date_range,
            data=[pmt]*len(self.date_range),
            columns=['salary']
        )
        # Consider adding columns for [salary, after-tax, after withholding, etc.]

        return df


    def plot_salary_pmts(self, **kwargs):
        self.cash_flows.resample('d').mean().cumsum().fillna(method='ffill').plot(**kwargs)


class CashSavings(Asset):
    def __init__(self, annualized_interest_rate):
        super().__init__('cash_savings')
        self.interest_rate = interest_rate
        self.contributions = []

    def add_contribution(self, amount, date, label, recurring=False, freq=None, periods=None):
        if not recurring:
            date_range = pd.date_range(
                start=date,
                periods=1,
                freq='D',
                normalize=True
            )
        else:
            date_range = pd.date_range(
                start=date,
                freq=freq,
                periods=periods,
                normalize=True
            )

        contrib = pd.DataFrame(
            index=date_range,
            data=[amount]*len(date_range),
            columns=[label]
        )

        self.contributions.append(contrib)

    @property
    def all_contributions(self):
        df = (
            pd.concat(self.contributions, axis=1)
            .fillna(0)
            .cumsum()
        )
        df['total_contributions'] = df.sum(axis=1)
        return df

#     @property
#     def daily_interest_rate(self):
#         """TO DO: Calc this the right way"""
#         return annualized_interest_rate/365

#     def interest_pmts(self):
#         """TO DO: Maybe this should be discrete like when the pmts are actually made? Doesn't matter for now"""
#         interest = self.daily_interest_rate
#         return  self.all_contributions.total_value

    def value_through_time(self):
        pass

    def value_at_a_given_point_in_time(self, dt):
        pass

    def expected_value_through_time(self, periods, freq='d'):
#         self.date_range = pd.date_range(
#             start=next_paycheck_dt,
#             periods=(years * self._annual_pmt_periods),
#             freq=self._pmt_freqs
#         )
        pass
