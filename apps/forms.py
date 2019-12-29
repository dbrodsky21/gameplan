import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from datetime import datetime as dt
import pandas as pd

# - Email
# - Birthday
#
# - salary
#     * Geo
#     * Current Annual salary
#     * Age
#     * Age Cohort
#     * Gender
#     * (or just percentile)
#     - (next raise)
# - tax rate
# - existing 401k
# - Cash savings (interest rate; adjustable)
# - 401k contributions (employer match)
# - (Pre-Tax Expenses)
# - Rent
# - Other expenses


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

dob_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Date of Birth", html_for="dob_input"),
            html.Div(
                dcc.DatePickerSingle(
                    id="dob_input",
                    date=dt(1985, 1, 1),
                    placeholder="MM/DD/YYYY",
                    # initial_visible_month=dt(1985, 1, 1),
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

gender_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Gender", html_for="gender_input"),
            dbc.RadioItems(
                id='gender',
                options=[
                    {'label': 'Female', 'value': 'Female'},
                    {'label': 'Male', 'value': 'Male'},
                    {'label': 'Neither', 'value': 'Neither'},
                    {'label': 'Prefer not to say', 'value': 'Prefer not to say'}
                ],
                # value='All',
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

DMAS = [
    'New York-Northern New Jersey-Long Island, NY-NJ-PA',
    'Los Angeles-Long Beach-Anaheim, CA',
    'Washington, DC/MD/VA',
    'Chicago-Naperville-Joliet, IL-IN-WI',
    'Boston-Cambridge-Newton, MA-NH',
    'Dallas-Fort Worth-Arlington, TX',
    'Philadelphia-Camden-Wilmington, PA/NJ/DE',
    'None of the these'
]

geo_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("Metro Area (DMA)", html_for="geo_input"),
            html.Div(
                dcc.Dropdown(
                    id='dma',
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
            dbc.Label("Current Income", html_for="salary_group"),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("$", addon_type="prepend"),
                    dbc.Input(
                        id="salary_input",
                        placeholder="Pre-tax income",
                        type="number",
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

## Probably want non-401k investments right?
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
                        value=0
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
                        value=0
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
                        value=0
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

layout = dbc.Container(
    [
        html.H1("Input Form"),
        html.H2("Subheader"),
        html.H3("H3"),
        dbc.Card(
            [
                dbc.CardHeader('Personal Info'),
                dbc.CardBody(
                    [
                        dbc.Row([email_input, dob_input]),
                        dbc.Row(geo_input),
                        dbc.Row(gender_input),
                    ]
                )
            ]
            , color="light"
            , style={'marginBottom': 20}
        ),
        dbc.Card(
            [
                dbc.CardHeader('Salary Info'),
                dbc.CardBody(
                    [
                        dbc.Row(salary_input),
                        dcc.Graph()
                    ]
                )
            ]
            , color="light"
            , style={'marginBottom': 20}
        ),
        dbc.Card(
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
        dbc.Card(
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
    ]
)
