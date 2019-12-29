import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from datetime import datetime as dt
import numpy as np
import pandas as pd

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
                    placeholder="MM/DD/YYYY",
                    # date=dt(1985, 1, 1),
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
                        value=0,
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


"""
##  Graphs
"""
income_dist_graph = dcc.Loading(
    id="loading-income-dist",
    children=[dcc.Graph(id="forms-income-dist-graph")],
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
                        dbc.Row(salary_input),
                        income_dist_graph
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
                        dbc.Row([existing_401k_input, ongoing_401k_contribution_input]),
                        dbc.Row([employer_401k_contribution_pct_input, employer_401k_contribution_rate_input]),
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
                        dbc.Row([housing_expense_input, non_housing_expense_input]),
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
     # some expensive clean data step
     cleaned_df = inc.get_cohort_subset(
        df=working_pop,
        dma=dma,
        age_range=age_range,
        gender=gender
        )

     # more generally, this line would be
     # json.dumps(cleaned_df)
     return cleaned_df.to_json(date_format='iso', orient='split')


@app.callback(
    Output(component_id='forms-income-dist-graph', component_property='figure'),
    [
        Input(component_id='geo_input', component_property='value'),
        Input('salary_input', 'value'),
        # Input('age_range', 'value'),
        Input('gender_input', 'value'),
    ],
)
def update_income_dist_figure(dma, salary, gender):
    fig, percentile = inc.get_income_dist_fig(
        df=working_pop,
        dma=dma,
        salary=salary,
        age_range= [27, 31], #age_range,
        gender=gender,
        return_pctile=True
        )
    # percentile_label = f"Within your cohort you fall into the {inc.get_percentile_label(percentile)} percentile"
    return fig


# 1. Create a user object
# 2. Get user's income percentile
# 3. Create a salary object using growth points from user
# 4. Create a portfolio
#     - init w/ initial savings (call back)
#     - init w/ interest rate (assumed)
# 5. Add salary to portfolio
# 6. Add 401k (initialized w/ existing 401k)
# 7. Add 401k contributions
# 8. Add non-401k investments?
# 9. Create rent expense
# 10. Create Misc expense

# from gameplan.user import User
#
# subset_df =
#
# user = User(
#     email=callback_email,
#     birthday=callback_email,
#     zip_code=geo,
#     gender=callback_gender,
#     # percentile=calculated_percentile
# )
# inc.get_income_percentile():
# def get_income_percentile()
# portfolio =
