import pandas as pd

INPUT_DIR = 'gameplan/growth/raw_data/'

class KitcesData():
    def __init__(self):
        self.cleaned_data = self._get_kitces_growth_curves()

    def _get_kitces_growth_curves(self):
        growth_curves = pd.read_csv(INPUT_DIR + 'Income Growth - To upload.csv')
        growth_curves['age_days'] = growth_curves.age.apply(
            lambda x: pd.Timedelta(x, 'Y').days
            )
        growth_curves.drop(columns=['age_bucket', 'age'], inplace=True)
        growth_curves.set_index('age_days', inplace=True)
        growth_curves.columns = [int(x) for x in growth_curves.columns]
        return growth_curves
