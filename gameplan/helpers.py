import pandas as pd


FREQ_MAP = {
    'Y': pd.DateOffset(years=1),
}


def get_offset_date(freq, ref_date=pd.datetime.today(), rollback=False):
    offset = pd.tseries.frequencies.to_offset(freq)
    if rollback:
        return offset.rollback(ref_date)
    else:
        return offset.rollforward(ref_date)
