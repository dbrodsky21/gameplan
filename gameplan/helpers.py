import pandas as pd


FREQ_MAP = {
    'Y': pd.DateOffset(years=1),
}


def get_next_date_offset(freq, ref_date=pd.datetime.today()):
    offset = pd.tseries.frequencies.to_offset(freq)
    return offset.rollforward(ref_date)
