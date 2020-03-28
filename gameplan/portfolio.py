import pandas as pd

from gameplan.assets import Assets, CashSavings
from gameplan.cashflows import CashFlow
from gameplan.gp_collections import Collection, CashFlowCollection
from gameplan.contributions import Contribution
from gameplan.expenses import Expense, Expenses
from gameplan.income_streams import IncomeStreams
from gameplan.liabilities import Liability


class Portfolio():
    def __init__(self, initial_cash_savings=0, annualized_interest_rate=0):
        init_cs = CashSavings(
            initial_balance=initial_cash_savings,
            annualized_interest_rate=annualized_interest_rate
            )
        self.assets = Assets(objects={'cash_savings': init_cs})
        self.liablities = Collection(collection_type=Liability, objects={})
        self.income_streams = IncomeStreams(income_streams={})
        self.expenses = Expenses(expenses={}) #+ ...

    def add_income_stream(self, income_stream, label=None, if_exists='error'):
        self.income_streams.add_object(income_stream, label, if_exists)

    def add_expense(self, expense, label=None, if_exists='error'):
        self.expenses.add_object(expense, label, if_exists)
        self.update_cash_savings() # TO DO: figure out if this crude solution actually works

    def remove_expense(self, label):
        self.expenses.remove_object(label)
        self.update_cash_savings() # TO DO: figure out if this crude solution actually works

    def add_pretax_expense(self, from_income_stream_label, amt, label=None, if_exists='error'):
        inc = self.income_streams.contents[from_income_stream_label]
        exp = Expense(expense_type=label, date_range=inc.date_range, amount=amt, recurring=True, pretax=True)
        inc.add_deduction(label=exp.name, amt=exp.amount, if_exists=if_exists)
        self.expenses.add_object(exp, label, if_exists)
        self.update_cash_savings() # TO DO: figure out if this crude solution actually works

    def remove_pretax_expense(self):
        # TO DO: do i need this?
        raise NotImplementedError

    def add_asset(self, asset, label=None, if_exists='error'):
        self.assets.add_object(asset, label, if_exists)

    def add_liability(self, liability, label=None, if_exists='error'):
        self.liabilities.add_object(liability, label, if_exists)

    def add_401k_contribution(self, income_stream_label, contrib_pct, employer_match=None, label='401k', if_exists='error'):
        """employer_match should be a dict w/ keys == {'upto', 'pct_match'}"""
        #TO DO: does this need a remove method as well?
        inc = self.income_streams.contents[income_stream_label]
        inc.add_deduction(label=label, pct=contrib_pct, if_exists=if_exists)
        employee_contrib = Contribution.from_income_stream(inc, pct=contrib_pct,
                                                           label=f'401k_employee_contribs_{contrib_pct:.1%}')
        # To Do: What happens if no 401k exists yet
        self.assets.contents['401k'].add_contribution(employee_contrib, if_exists=if_exists)

        if employer_match:
            upto = employer_match['upto']
            pct_match = employer_match['pct_match']
            match_pct = min(contrib_pct, upto) * pct_match
            employer_contrib = Contribution.from_income_stream(inc, pct=match_pct,
                                                               label=f'401k_employer_contribs_{match_pct:.1%}')
            self.assets.contents['401k'].add_contribution(employer_contrib, if_exists=if_exists)

        self.update_cash_savings() # TO DO: figure out if this crude solution actually works

    @property
    def net_cashflows(self):
        inflows = self.income_streams.contents['salary'].take_home_salary
        outflows = Expenses(expenses=self.expenses.post_tax).total
        net = pd.concat([inflows, outflows], axis=1).fillna(0).sum(axis=1)
        return pd.Series(net, name='net_cashflows')

    def update_cash_savings(self):
        # TO DO: Think through this, I'm overwriting stuff every time I call this which seems wrong
        cs = self.assets.contents['cash_savings']
        inflows = self.income_streams.contents['salary'].take_home_salary
        cs.add_contribution(Contribution('cash_inflows', date_range=inflows.index, values=inflows.values),
                            if_exists='overwrite')
        outflows = Expenses(self.expenses.post_tax)
        total_outflows = outflows.get_total_as_cashflow(freq='D', name='cash_outflows')
        if outflows.contents:
            cs.add_debit(total_outflows, if_exists='overwrite')

    @property
    def cash_savings(self):
        self.update_cash_savings()
        cs = self.assets.contents['cash_savings']
        return cs.value_through_time

    @property
    def all_cashflows(self):
        return CashFlowCollection(
            collection_type=CashFlow,
            objects=[
                # self.income_streams_from_assets,
                # self.debt_service_from_liabilities,
                self.income_streams.contents,
                self.expenses.contents
            ]
        )
#     @property
#     def income_streams_from_assets(self):
#         ## You may wanna rip out the interest accumulation from CashSavings, put that as a property on Assets
#         ## or at least interest bearing assets
#         pass
#
#     @property
#     def debt_service_from_liabilities(self):
#         pass
#
#
#     @property
#     def portfolio_pv(self): # aka net_worth?
# #         assets.pv + liabilibilities.pv + income_streams.pv + expenses.pv
#         pass
#
#
#     def simulate_portfolio_value(self):
#         pass
#
#     def plot_portfolio_value(self):
#         pass

    #TO DO: Each of these functions should probs be defined at the IncomeStream/Asset/Liability/Expense level as well?
    #TO DO: Add functionality to add objects to each of the gp_collections (i.e. add asset/liability//etc.)
