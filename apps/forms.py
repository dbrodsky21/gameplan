import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from datetime import datetime as dt
import numpy as np
import pandas as pd
import plotly.express as px
import scipy.stats as sp

from gameplan.assets import Equity
from gameplan.expenses import Expenses, Rent, MiscellaneousExpenses
from gameplan.user import User
from gameplan.income_streams import Salary
from gameplan.portfolio import Portfolio
from gameplan.growth.growth_models import KitcesIncomeGrowthModel

# from gameplan.growth.income_percentile_estimate import get_working_population_data
# from apps.income_forecast import get_income_dist_fig, get_income_trajectory_fig
import apps.income_forecast as inc

from dash.dependencies import Input, Output, State

from app import app

"""
#  Constants
"""
working_pop = inc.get_working_population_data()
DMAS = [
    'New York-Northern New Jersey-Long Island, NY-NJ-PA',
    'Los Angeles-Long Beach-Anaheim, CA',
    'Washington, DC/MD/VA',
    'Chicago-Naperville-Joliet, IL-IN-WI',
    'Boston-Cambridge-Newton, MA-NH',
    'Dallas-Fort Worth-Arlington, TX',
    'Philadelphia-Camden-Wilmington, PA/NJ/DE',
    'None of these'
]

"""
#  Layout Components
"""

"""
##  Inputs
"""
email_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Email", html_for="email_input"),
            dbc.Input(
                type="email", id="email_input", placeholder="Enter email"
            )
        ],
    )
)

# TO DO: Consider adding an age cohort bar below this
dob_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Date of Birth", html_for="dob_input"),
            html.Div(
                dcc.DatePickerSingle(
                    id="dob_input",
                    # placeholder="MM/DD/YYYY",
                    date=dt(1985, 1, 1),
                    initial_visible_month=dt(1985, 1, 1),
                    # with_portal=True,
                    # number_of_months_shown=1,
                    style={'justifyContent':'start'}
                ),
                className="dash-bootstrap"
            ),
            dbc.FormText(
                "Type as MM/DD/YYYY or choose from pop-out",
                color="secondary",
            ),
        ],
    )
)

age_cohort_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Relevant Age Cohort", html_for="age_cohort_input"),
            html.Div(
                dcc.RangeSlider(
                    id='age_cohort_input',
                    count=1,
                    min=22,
                    max=65,
                    step=1,
                    value=[23, 27],
                    marks={
                        20: "20",
                        25: "25",
                        30: "30",
                        35: "35",
                        40: "40",
                        45: "45",
                        50: "50",
                        55: "55",
                        60: "60",
                        65: "65",
                    },
                    tooltip={'placement': 'bottom'}
                ),
                className="dash-bootstrap"
            ),
            dbc.FormText(
                (
                    f'If you like, adjust the age range of individuals you would ',
                    f'consider your "peers". This will be used for estimating your ',
                    f'income percentile within your cohort. Default is your age +/- 2 years.'
                ),
                color="secondary",
            ),
        ],
    )
)

gender_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Gender", html_for="gender_input"),
            dbc.RadioItems(
                id='gender_input',
                options=[
                    {'label': 'Female', 'value': 'Female'},
                    {'label': 'Male', 'value': 'Male'},
                    {'label': 'Neither', 'value': 'Neither'},
                    {'label': 'Prefer not to say', 'value': 'Prefer not to say'}
                ],
                value='Prefer not to say',
                inline=True
                # labelStyle={'display': 'inline-block'}
            ),
            dbc.FormText(
                "Which gender do you identify as?",
                color="secondary",
            ),
        ],
    )
)

geo_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Metro Area (DMA)", html_for="geo_input"),
            html.Div(
                dcc.Dropdown(
                    id='geo_input',
                    options=[{'label': dma, 'value': dma} for dma in DMAS],
                    value='New York-Northern New Jersey-Long Island, NY-NJ-PA',
                    # clearable=False,
                    # style={"marginBottom": 0, "font-size": 12},
                ),
                className="dash-bootstrap"
            ),
            dbc.FormText(
                "Which metro area do you live in? If you can't find your city, choose 'None of these'",
                color="secondary",
            ),
        ],
    )
)

salary_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Current Total Pre-Tax Income", html_for="salary_group"),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("$", addon_type="prepend"),
                    dbc.Input(
                        id="salary_input",
                        placeholder="Pre-tax income",
                        type="number",
                        value=10000,
                        min=0,
                        step=1000,
                    ),
                ],
                id='salary_group',
                className="mb-3",
            ),
            dbc.FormText(
                "Enter your current annual pre-tax income",
                color="secondary",
            ),
        ],
    )
)

cash_savings_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Current Cash Savings", html_for="cash_savings_group"),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("$", addon_type="prepend"),
                    dbc.Input(
                        id="cash_savings_input",
                        # placeholder="Enter your existing cash savings",
                        type="number",
                        value=0,
                        min=0,
                        step=1000,
                    ),
                ],
                id='cash_savings_group',
                className="mb-3",
            ),
            dbc.FormText(
                "I.e. what's readily available in your checking / savings accounts? An approximation is totally fine.",
                color="secondary",
            ),
        ],
    )
)

# Think rather than 401k / non this should be taxable / non-taxable maybe?
non_401k_investments_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Current Investments (Non-401k)", html_for="non_401k_investments_group"),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("$", addon_type="prepend"),
                    dbc.Input(
                        id="non_401k_investments_input",
                        # placeholder="Enter your existing cash savings",
                        type="number",
                        value=0,
                        min=0,
                        step=1000,
                    ),
                ],
                id='non_401k_investments_group',
                className="mb-3",
            ),
            dbc.FormText(
                "What's the current approximate value of your investments outside your 401k / Roth IRA, if any?",
                color="secondary",
            ),
        ],
    )
)

future_non_401k_investments_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Future Investments (Non-401k)", html_for="future_non_401k_investments_group"),
            dbc.InputGroup(
                [
                    dbc.Input(
                        id="future_non_401k_investments_input",
                        # placeholder="Enter your existing cash savings",
                        type="number",
                        value=0,
                        min=0,
                        max=100,
                        step=1,
                    ),
                    dbc.InputGroupAddon("%", addon_type="append"),
                ],
                id='future_non_401k_investments_group',
                className="mb-3",
            ),
            dbc.FormText(
                "Outside of your 401k, what proportion of your salary do you plan on investing on an ongoing basis?",
                color="secondary",
            ),
        ],
    )
)

existing_401k_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Existing 401k Investments", html_for="existing_401k_group"),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("$", addon_type="prepend"),
                    dbc.Input(
                        id="existing_401k_input",
                        # placeholder="Approximate value of your ",
                        type="number",
                        value=0,
                        min=0,
                        step=1000,
                    ),
                ],
                id='existing_401k_group',
                className="mb-3",
            ),
            dbc.FormText(
                "What's the approximate value of your 401k investments *today*?",
                color="secondary",
            ),
        ],
    )
)

ongoing_401k_contribution_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Future 401k Contribution", html_for="ongoing_401k_contribution_group"),
            dbc.InputGroup(
                [
                    dbc.Input(
                        id="ongoing_401k_contribution_input",
                        type="number",
                        min=0,
                        max=100,
                        step=1,
                        value=0,
                    ),
                    dbc.InputGroupAddon("%", addon_type="append"),
                ],
                id='ongoing_401k_contribution_group',
                className="mb-3",
            ),
            dbc.FormText(
                "What proportion of your salary do you plan on contributing to your 401k on an ongoing basis?",
                color="secondary",
            ),
        ],
    )
)

employer_401k_contribution_pct_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Employer 401k Contribution Percentage", html_for="employer_401k_contribution_pct_group"),
            dbc.InputGroup(
                [
                    dbc.Input(
                        id="employer_401k_contribution_pct_input",
                        type="number",
                        min=0,
                        max=100,
                        step=1,
                        value=0,
                    ),
                    dbc.InputGroupAddon("%", addon_type="append"),
                ],
                id='employer_401k_contribution_pct_group',
                className="mb-3",
            ),
            dbc.FormText(
                "Up to what proportion of your 401k contribution does your employer match? If they don't match, keep at 0%",
                color="secondary",
            ),
        ],
    )
)

employer_401k_contribution_rate_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Employer 401k Contribution Rate", html_for="employer_401k_contribution_rate_group"),
            dbc.InputGroup(
                [
                    dbc.Input(
                        id="employer_401k_contribution_rate_input",
                        type="number",
                        min=0,
                        max=100,
                        step=1,
                        value=100,
                    ),
                    dbc.InputGroupAddon("%", addon_type="append"),
                ],
                id='employer_401k_contribution_rate_group',
                className="mb-3",
            ),
            dbc.FormText(
                "At what rate does your employer match your contribution? \
                 E.g. if for every $2 you contribute, your employer contributes $1 \
                 enter 50%."
                 ,
                color="secondary",
            ),
        ],
    )
)

housing_expense_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Housing Expenses", html_for="housing_expense_group"),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("$", addon_type="prepend"),
                    dbc.Input(
                        id="housing_expense_input",
                        # placeholder="Approximate value of your ",
                        type="number",
                        value=0,
                        min=0,
                        step=100,
                    ),
                    dbc.InputGroupAddon("per month", addon_type="append"),
                ],
                id='housing_expense_group',
                className="mb-3",
            ),
            dbc.FormText(
                "About how much do you pay for housing (rent & utilities) per month?",
                color="secondary",
            ),
        ],
    )
)

non_housing_expense_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Non-Housing Expenses", html_for="non_housing_expense_group"),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("$", addon_type="prepend"),
                    dbc.Input(
                        id="non_housing_expense_input",
                        # placeholder="Approximate value of your ",
                        type="number",
                        value=0,
                        min=0,
                        step=100,
                    ),
                    dbc.InputGroupAddon("per month", addon_type="append"),
                ],
                id='non_housing_expense_group',
                className="mb-3",
            ),
            dbc.FormText(
                "Approximately how much are your non-housing-related expenses \
                (e.g. food, entertainment, travel, clothing, etc.) each month? \
                You can ballpark it based on your last few credit card statements.",
                color="secondary",
            ),
        ],
    )
)

income_percentile_for_growth_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Income Percentile For Growth Scenarios", html_for="income_percentile_for_growth_group"),
            html.Div(
                dcc.Slider(
                    id='income_percentile_for_growth_input',
                    # count=1,
                    min=10,
                    max=90,
                    step=10,
                    value=50,
                    marks={
                        10: "10",
                        20: "20",
                        30: "30",
                        40: "40",
                        50: "50",
                        60: "60",
                        70: "70",
                        80: "80",
                        90: "90",
                    },
                    tooltip={'placement': 'bottom'}
                ),
                className="dash-bootstrap"
            ),
            dbc.FormText(
                (
                    f"This is for growth scenarios "
                ),
                color="secondary",
            ),
        ],
    )
)

"""
## Output
"""
income_percentile_text = dbc.Col(
    dbc.FormGroup(
        html.Div([
            dcc.Markdown(f"Among members of your cohort (people similar in age and location) you're currently in the:"),
            dcc.Markdown(f"___ Percentile in terms of total annual income", id='percentile_text', style={'textAlign':'center', "font-size": 20}),
            # dcc.Markdown(f"in terms of total annual income")
        ]),
    )
)

"""
##  Graphs
"""
income_trajectory_graph = dcc.Loading(
    id="loading-income-trajectory",
    children=[dcc.Graph(id="forms-income-trajectory-graph")],
    type="default",
)
expenses_trajectory_graph = dcc.Loading(
    id="loading-expenses-trajectory",
    children=[dcc.Graph(id="forms-expenses-trajectory-graph")],
    type="default",
)

savings_graph = dcc.Loading(
    id="loading-savings",
    children=[dcc.Graph(id="forms-savings-graph")],
    type="default",
)

"""
##  Overall Layout
"""
layout = dbc.Container(
    [
        html.H1("Input Form"),
        html.H2("Subheader"),
        html.H3("H3"),
        dbc.Card(id='personal_info_card', children=
            [
                dbc.CardHeader('Personal Info'),
                dbc.CardBody(
                    [
                        dbc.Row([email_input, dob_input]),
                        dbc.Row(age_cohort_input),
                        dbc.Row(geo_input),
                        dbc.Row(gender_input),
                    ]
                )
            ]
            , color="light"
            , style={'marginBottom': 20}
        ),
        dbc.Card(id='salary_info_card', children=
            [
                dbc.CardHeader('Salary Info'),
                dbc.CardBody(
                    [
                        dbc.Row([
                            salary_input,
                            income_percentile_text,
                            income_percentile_for_growth_input
                        ]),
                        income_trajectory_graph
                    ]
                )
            ]
            , color="light"
            , style={'marginBottom': 20}
        ),
        dbc.Card(id='expenses_card', children=
            [
                dbc.CardHeader('Expenses'),
                dbc.CardBody(
                    [
                        dbc.Row([
                            housing_expense_input,
                            non_housing_expense_input
                        ]),
                        expenses_trajectory_graph,
                    ]
                )
            ]
            , color="light"
            , style={'marginBottom': 20}
        ),
        dbc.Card(id='saving_and_investments_card', children=
            [
                dbc.CardHeader('Savings & Investments'),
                dbc.CardBody(
                    [
                        dbc.Row([cash_savings_input, non_401k_investments_input]),
                        dbc.Row(future_non_401k_investments_input),
                        savings_graph,
                        dbc.Row([existing_401k_input, ongoing_401k_contribution_input]),
                        dbc.Row([employer_401k_contribution_pct_input, employer_401k_contribution_rate_input]),
                    ]
                )
            ]
            , color="light"
            , style={'marginBottom': 20}
        ),


        # Hidden div inside the app that stores the intermediate value
        html.Div(id='cohort-df', style={'display': 'none'})
    ]
)

"""
## Helper Functions
"""

def create_portfolio(email, dob, dma, inc_pctile, salary, housing_exp,
                     non_housing_exp, initial_savings, current_investments,
                     existing_401k_val, ongoing_401k_contrib_pct,
                     employer_401k_pct, employer_401k_rate,):
    user = User(
        email=email,
        birthday=pd.datetime.fromisoformat(dob),
        zip_code=dma,
        income_percentile=inc_pctile
    )
    sal_grwth_points = user.get_growth_points_to_fit(
        growth_model=KitcesIncomeGrowthModel,
        start_dt=pd.datetime.today()
    )

    s = Salary(
        salary,
        payday_freq='Y',
        growth_points_to_fit=sal_grwth_points,
        last_paycheck_dt= user.birthday + pd.DateOffset(years=65),
        tax_rate=.35
    )

    port = Portfolio(initial_cash_savings=initial_savings, annualized_interest_rate=0.005)
    port.add_income_stream(s, label='salary', if_exists='overwrite')

    retirement_dt = pd.to_datetime(dob) + pd.DateOffset(years=65)
    port.add_expense(
        Rent(housing_exp, end_dt=retirement_dt),
        label='housing expenses',
        if_exists='overwrite'
    )
    port.add_expense(
        MiscellaneousExpenses(non_housing_exp, end_dt=retirement_dt),
        label='non-housing expenses',
        if_exists='overwrite'
    )

    investments = Equity(init_value=current_investments)
    port.add_asset(investments, label='investments', if_exists='overwrite')

    # future_investments = Equity(init_value=current_investments)
    # port.add_asset(future_investments, label='future_investments', if_exists='overwrite')

    # if existing_401k_val >= 0:
    existing_401k = Equity(init_value=existing_401k_val)
    port.add_asset(existing_401k, label='401k', if_exists='overwrite')

    if any([ongoing_401k_contrib_pct, employer_401k_pct]):
        port.add_401k_contribution(
            income_stream_label='salary',
            contrib_pct=ongoing_401k_contrib_pct,
            employer_match=dict(upto=employer_401k_pct, pct_match=employer_401k_rate),
            label='401k'
        )

    return port

"""
#  Callbacks
"""
@app.callback(
    Output('age_cohort_input', 'value'),
    [Input('dob_input', 'date')]
    )
def set_age_buckets(dob):
    age_days = (pd.datetime.today() - pd.to_datetime(dob)).days
    age_years =  np.floor(age_days / 365)
    return [age_years - 2, age_years + 2]

@app.callback(
    Output('cohort-df', 'children'),
    [
        Input(component_id='geo_input', component_property='value'),
        Input('salary_input', 'value'),
        Input('age_cohort_input', 'value'),
        Input('gender_input', 'value'),
    ]
    )
def get_cohort_df(dma, salary, age_range, gender):
     cleaned_df = inc.get_cohort_subset(
        df=working_pop,
        dma=dma,
        age_range=age_range,
        gender=gender
        )

     return cleaned_df.to_json(date_format='iso', orient='split')

@app.callback(
    Output(component_id='forms-income-trajectory-graph', component_property='figure'),
    [
        # Input(component_id='cohort-df', component_property='children'),
        Input('salary_input', 'value'),
        Input('dob_input', 'date'),
        Input('income_percentile_for_growth_input', 'value'),
    ],
)
def update_income_trajectory_figure(salary, dob, percentile):
    # cohort_df = pd.read_json(cohort_json, orient='split')
    age_days = (pd.datetime.today() - pd.to_datetime(dob)).days
    age_years =  np.floor(age_days / 365)
    fig = inc.get_income_trajectory_fig(
        salary=salary,
        age=age_years,
        income_percentile=percentile
        )
    return fig

@app.callback(
    [
        Output('percentile_text', 'children'),
        Output('income_percentile_for_growth_input', 'value'),
    ],
    [
        Input('cohort-df', 'children'),
        Input('salary_input', 'value'),
    ]
)
def update_percentile_text(cohort_json, salary):
    cohort_df = pd.read_json(cohort_json, orient='split')
    perc = sp.percentileofscore(cohort_df.inctot, salary)
    for_text = f"**{inc.get_percentile_label(perc)} percentile** in terms of total annual income"
    return for_text, inc.get_pctile_for_growth(perc)

@app.callback(
    Output(component_id='forms-expenses-trajectory-graph', component_property='figure'),
    [
        # Input(component_id='cohort-df', component_property='children'),
        Input('housing_expense_input', 'value'),
        Input('non_housing_expense_input', 'value'),
        Input('dob_input', 'date'),
    ],
)
def update_expenses_trajectory_figure(housing_expense, non_housing_expense, dob):
    # cohort_df = pd.read_json(cohort_json, orient='split')
    age_days = (pd.datetime.today() - pd.to_datetime(dob)).days
    age_years =  np.floor(age_days / 365)
    retirement_dt = pd.to_datetime(dob) + pd.DateOffset(years=65)
    exp = Expenses(expenses={
        'housing': Rent(housing_expense, end_dt=retirement_dt),
        'non-housing': MiscellaneousExpenses(non_housing_expense, end_dt=retirement_dt)
    })
    fig = px.line((-1*exp.as_df).stack().reset_index(), x='level_0', y=0, color='level_1')
    return fig


@app.callback(
    Output('forms-savings-graph', 'figure'),
    [
        Input('email_input', 'value'),
        Input('dob_input', 'date'),
        Input('geo_input', 'value'),
        Input('income_percentile_for_growth_input', 'value'),
        Input('salary_input', 'value'),
        Input('housing_expense_input', 'value'),
        Input('non_housing_expense_input', 'value'),
        Input('cash_savings_input', 'value'),
        Input('non_401k_investments_input', 'value'),
        Input('existing_401k_input', 'value'),
        Input('ongoing_401k_contribution_input', 'value'),
        Input('employer_401k_contribution_pct_input', 'value'),
        Input('employer_401k_contribution_rate_input', 'value'),
    ]
)
def update_savings_graph(email, dob, dma, inc_pctile, salary, housing_exp,
                         non_housing_exp, initial_savings, current_investments,
                         existing_401k, ongoing_401k_contrib_pct,
                         employer_401k_pct, employer_401k_rate):

    port = create_portfolio(email, dob, dma, inc_pctile, salary, housing_exp,
                            non_housing_exp, initial_savings,
                            current_investments, existing_401k,
                            ongoing_401k_contrib_pct/100,
                            employer_401k_pct/100, employer_401k_rate/100)

    # to_plt = port.assets.generate_path_df().reset_index().melt(id_vars='index')
    # return px.line(to_plt, x='index', y='value', color='variable')
    to_plt = port.assets.contents['401k'].simulate_path().reset_index()
    return px.line(to_plt, x='index', y='total_value')
