import pandas as pd
import re


FREQ_MAP = {
    'Y': pd.DateOffset(years=1),
}


def get_offset_date(freq, ref_date=pd.datetime.today(), rollback=False):
    offset = pd.tseries.frequencies.to_offset(freq)
    if rollback:
        return offset.rollback(ref_date)
    else:
        return offset.rollforward(ref_date)


def combine_list_of_dicts(L):
    "TO DO: Make this clearer"
    return {k: v for d in L if d is not None for k, v in d.items()}


def to_snake_case(s):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def compound_interest(principal, rate, times_per_year, years):
    # (1 + r/n)
    body = 1 + (rate / times_per_year)
    # nt
    exponent = times_per_year * years
    # P(1 + r/n)^nt
    return principal * pow(body, exponent)
