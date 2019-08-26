rom gameplan.assets import Assets, CashSavings
from gameplan.expenses import Expenses
from gameplan.income_streams import IncomeStreams
from gameplan.liabilities import Liability


class Portfolio():
    def __init__(self, initial_cash_savings=0, interest_rate=0):
        init_cs = CashSavings(
            initial_balance=initial_cash_savings,
            annualized_interest_rate=interest_rate
            )
        self.assets = Assets(objects=dict(initial_savings=init_cs))
        self.liablities = Collection(collection_type=Liability, objects={})
        self.income_streams = IncomeStreams(income_streams={}) # includes salary, etc.
        self.consumption = Expenses(expenses={}) #+ ...

    def add_income_stream(self, income_stream, label=None, if_exists='error'):
        self.income_streams.add_object(income_stream, label, if_exists)

    def add_expense(self, expense, label=None, if_exists='error'):
        self.consumption.add_object(expense, label, if_exists)

    def add_asset(self, asset, label=None, if_exists='error'):
        self.assets.add_object(asset, label, if_exists)

    def add_liability(self, liability, label=None, if_exists='error'):
        self.liabilities.add_object(liability, label, if_exists)


    @property
    def income_streams_from_assets(self):
        ## You may wanna rip out the interest accumulation from CashSavings, put that as a property on Assets
        ## or at least interest bearing assets
        pass

    @property
    def debt_service_from_liabilities(self):
        pass


    @property
    def all_cashflows(self):
        return CashFlowCollection(
            collection_type=CashFlow,
            objects=[
                self.income_streams_from_assets,
                self.debt_service_from_liabilities,
                self.income_streams.contents,
                self.consumption.contents
            ]
        )


    @property
    def portfolio_pv(self): # aka net_worth?
#         assets.pv + liabilibilities.pv + income_streams.pv + consumption.pv
        pass


    def simulate_portfolio_value(self):
        pass

    def plot_portfolio_value(self):
        pass

    #TO DO: Each of these functions should probs be defined at the IncomeStream/Asset/Liability/Expense level as well?
    #TO DO: Add functionality to add objects to each of the collections (i.e. add asset/liability//etc.)
