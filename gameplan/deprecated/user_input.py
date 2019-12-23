import pandas as pd
import numpy as np
import shelve
from textwrap import dedent

from gameplan.user import User
from gameplan.datamodel import *
from gameplan import paths


def greet_user():
    print("Hi! Today we're gonna... Let's get started!\n")

def convert_to_number(user_input):
    if '%' in user_input:
        return float(user_input.strip('%')) / 100
    elif float(user_input) > 1:
        return float(user_input) / 100
    else:
        return float(user_input)


def get_user_object():
    print("Please enter your email address")
    email = input().lower()
    # Check users_db for record, if exists load, else create new user
    with shelve.open(paths.USERS_DB_PATH, 'c') as user_db:
        user_id = User.get_user_id(email)
        if user_id in user_db:
            user = user_db[user_id]
            print("Hey {}, we've found your record and have loaded your profile!"
            .format(user.email))
        else:
            user = User(email)
            print(dedent("""
            Great! All progress in this session will be saved. Whenever you like
            you can tell us to "forget" your info and we'll delete your record
            from our database.

            Your privacy is our #1 concern.\n
            """))

    return user

def get_user_demography(user):
    print("How old are you?")
    user.age = input()
    # print("When do you want to retire?")

def get_income_streams():
    pass

def collect_salary_info():
    print("\nHow much do you earn before taxes? (Enter whatever's easiest: per week/month/year)")
    salary = input()
    print("\nIs that per week, month, or year?")
    sal_fmt = input()
    print("\nHow often do you get paid? [Select what's closest: weekly, bi-weekly, twice monthly, monthly")
    sal_freq = input()
    print("\nWhen's your next paycheck? (Please enter in YYYY-MM-DD format)")
    next_paycheck_dt = pd.datetime.strptime(input(), '%Y-%m-%d')

    ## I'm not sure I wanna be storing these in a list; income stream object?
    return Salary(salary, sal_fmt, 'twice monthly', next_paycheck_dt, years=1)
    # user.income_streams.append(user.salary)

def estimate_tax_rate():
    return .35

def get_tax_rate():
    ## This should be user-level characteristic right?
    estimated_tax_rate = estimate_tax_rate()
    print(dedent("""
    \nWe estimate your tax rate is {:.0%}, would you like to change this estimate?
    (If so, please enter a %, otherwise skip)
    """.format(estimated_tax_rate)))
    user_input = input()
    return convert_to_number(user_input) if user_input else estimated_tax_rate

def get_salary_info(user):
    print("\nAre you currently earning a salary? [Type: Yes or No]")
    if 'n' in input().lower():
        print("Get a job hippie!")
        return None

    user.salary = collect_salary_info()
    user.save_user()
    tax_rate = get_tax_rate()
    user.salary.tax_withholding_rate = tax_rate
    # user.tax_rate = tax_rate
    print(dedent("""
    Based on these inputs we estimate that you're taking home about ${:,.0f}
    from every {} paycheck, or ${:,.0f} a year.
    """.format(
        user.salary.cash_flow,
        user.salary.payday_freq,
        user.salary.salary_annualized*(1-user.salary.tax_withholding_rate)
    )))
    user.save_user()

    # print("""That looks kinda like this:""")
    # user.salary.plot_salary_pmts(figsize=(24,12))
    pass

def get_expenses(user):
    print("\nDo you rent or own your residence? (Type 'rent' or 'own')")
    if input() == 'rent':
        print("\nHow much is your rent per month?")
        rent = Rent( float( input() ) )
        user.expenses.append(rent)
    elif input() == 'own':
        pass
    else:
        raise ValueError()

    print("\nHow much are your utilities per month?")
    utilities = Utilities(float(input()))
    user.expenses.append(utilities)

    print("\nWhat about other (consistent) miscellaneous expenses in a given month?")
    addtl_exp = Expense('other', float(input()), freq='M')
    user.expenses.append(addtl_exp)

    user.save_user()

def main():
    greet_user()
    user = get_user_object()
    # if not user.salary:
    get_salary_info(user)
    print("Lets try to understand where that goes:")
    get_expenses(user)

    print(dedent("""
    Alright, after expenses it seems like you have ${:,.0f} left over per month
    """.format(
        user.agg_net_cash_flows(freq='M').mean()
        )))
    print("""
    We can either assume that money goes into a savings account or you can give us some more details on where you think it's going.\n
    Please check all that apply:
    * Savings
    * Investment
    * Paying down debt, e.g. [Student, credit card, (mortgage?)]
    * Consumption
        - Clothes
        - Alcohol
        - Restaurants/bars
        - Entertainment, e.g. movies, baseball games,
        - Other: [     ]
    """)
    print("Do you want to tell us more about any of those? [Yes | No]")
    return user


if __name__ == "__main__":
    main()
