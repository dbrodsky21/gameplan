import pandas as pd

def get_next_date_offset(freq, ref_date=pd.datetime.today()):
    offset = pd.tseries.frequencies.to_offset(freq)
    return offset.rollforward(ref_date)
