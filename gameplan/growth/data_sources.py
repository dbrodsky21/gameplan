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

class USDAData():
    def __init__(self):
        """
        Child expenditure data from USDA report "Expenditures on Children by
        Families, 2015", see:
            * Original - https://fns-prod.azureedge.net/sites/default/files/crc2015_March2017.pdf
            * Gsheets - https://docs.google.com/spreadsheets/d/1pXaXiWU93WuAM93rrYMzewR_cWWGno0cJYPLakz_bYA/edit?usp=sharing
        """
        self.cleaned_data = self._clean_data()
        self.growth_curves = self._get_growth_curves()

    def _clean_data(self):
        CSV = 'USDA Expenditures on Children by Families, 2015 - Assembled.csv'
        raw = pd.read_csv(INPUT_DIR + CSV)

        EXP_COLS = [x for x in raw.columns if '_exp' in x] # get expenses columns

        # Each row has a start_ and end_age, we want it in days to pass to our growth series
        raw['end_age_days'] = raw.end_age.apply(
            lambda x: pd.Timedelta(x, 'Y').days
            )
        grouped = (
            raw
            #get rid of the 'totals' row and the data for single parent households (too complicated for now)
            .query('age_group != "0 - 17" & family_status == "Married"')
            .groupby(['end_age_days', 'geo', 'income_group'])
            [EXP_COLS]
            .mean()
            .stack()
            .unstack([1, 2, 3]) # columns now an heirarchical index ['geo', 'inc', 'expense_type']
        )
        grouped.loc[0] = grouped.loc[raw.end_age_days.min()] # fill in expenses at day 0
        grouped.sort_index(inplace=True)

        return grouped

    def _get_growth_curves(self):
        df = self.cleaned_data
        # Normalize to % growth rather than absolute levels
        growth_curves = df.divide(df.loc[0])

        return growth_curves
