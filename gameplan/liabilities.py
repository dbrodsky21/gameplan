import pandas as pd
import numpy as np

from gameplan.cashflows import CashFlow

class InterestRateSeries():
    @staticmethod
    def get_index_rates(index_name_or_ticker=None):
        # check if index is a ticker or the name of an index
        # Map to ticker
        # Get time series of those rates
        # Needs to return a pd.Series() (that fits w/ self.date_range?)
        raise NotImplementedError("")

    def __init__(self, spread, name='Interest Rate', rate_type='fixed', index=None,
                 start_dt=None, end_dt=None, freq='D'):
        self.name = name
        self.start_dt = start_dt if start_dt else hp.get_offset_date(freq)
        self.end_dt = end_dt if end_dt else hp.get_offset_date(
            freq, ref_date=pd.datetime.today() + pd.DateOffset(years=50), rollback=True
        ) # Should have a function for establishing default end_dts that checks against start_dt
        self.spread = spread
        self.rate_type = rate_type
        self.index = index
        self.freq = freq

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
    def index_rates(self):
        return self.get_index_rates(self.index) if self.index else None

    @property
    def interest_rates(self):
        index_rates = self.index_rates if self.index_rates else pd.Series([0] * len(self.date_range))
        interest_rates = index_rates + self.spread

        return interest_rates.values

    @property
    def interest_rates_df(self):
        """A pandas dataframe representing the interest rate at each point in time
        """
        rates_df = pd.DataFrame(
            index=self.date_range,
            data=self.interest_rates,
            columns=[self.name]
        )

        return rates_df

class Liability():
    def __init__(self, liability_type):
        self.liability_type = liability_type

    def get_debt_service_cost(self):
        pass


class StudentDebt():
    def __init__(self, principal_outstanding, interest_rate_spread, interest_rate_type='fixed',

                 interest_rate_index=None, prepayment_penalty=None, payment_freq='MS', start_dt=None):

        self.liability_type = 'student_debt'
        self.name = 'NYU'
        self.principal_outstanding = principal_outstanding
        self.start_dt = start_dt if start_dt else hp.get_offset_date(payment_freq)
        self.interest_rate = InterestRateSeries( # Should this be annualized or something?
            rate_type=interest_rate_type,
            spread=interest_rate_spread,
            index=interest_rate_index,
            start_dt=None,
            end_dt=None,
            freq=payment_freq
        )
        self.prepayment_penalty = prepayment_penalty
        self.payment_freq = payment_freq
        self.minimum_pmt = minimum_pmt
        self.repayment_period = repayment_period

    def get_pmt_schedule(self, pmt_amount):
        start_dt = self.start_dt
        # Translate annualized interest rate into interest rate btwn payments
        # Deduct pmt amount from principal each month
        # Add interest payment

        pass
