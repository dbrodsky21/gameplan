import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from datetime import datetime as dt
from functools import reduce
import numpy as np
import pandas as pd
from plotly import graph_objects as go
import plotly.express as px
from typing import List, Optional


from gameplan.growth.data_sources import USDAData

from dash.dependencies import Input, Output, State

from app import app

"""
#  Constants
"""
REGIONS = [
    'Urban Northeast',
    'Urban West',
    'Urban Midwest',
    'Urban South',
    'Overall United States',
    'Rural',
]
INCOME_GROUPS = [
    '< $59,200',
    '$59,200 to $107,400',
    '> $107,400',
]
DATA = USDAData()

"""
#  Layout Components
"""

"""
##  Inputs
"""
region_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("In which region do you live?", html_for="region_input"),
            html.Div(
                dcc.Dropdown(
                    id='region_input',
                    options=[{'label': region, 'value': region} for region in REGIONS],
                    value='Urban Northeast',
                ),
                className="dash-bootstrap"
            ),
            dbc.FormText(
                "The cost of raising children varies a lot across regions.",
                color="secondary",
            ),
        ],
    )
)

income_group_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("What is your current household income?", html_for="income_group"),
            html.Div(
                dcc.Dropdown(
                    id='income_group_input',
                    options=[{'label': grp, 'value': grp} for grp in INCOME_GROUPS],
                    value=INCOME_GROUPS[0],
                ),
                className="dash-bootstrap"
            ),
            dbc.FormText(
                "Households of differing incomes tend to have dramatically different child-rearing costs.",
                color="secondary"
            ),
        ],
    )
)

n_existing_children_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("How many children under 18 do you have?",
                      html_for="n_existing_children_group"),
            html.Div(
                dcc.Dropdown(
                    id='n_existing_children_input',
                    options=[ {'label': n, 'value': n} for n in range(5) ],
                    value=0,
                    className="mb-3",
                ),
                className="dash-bootstrap"
            ),
        ],
        id='n_existing_children_group',
        className="mb-3",
    )
)

existing_children_ages_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("How old are they? Enter their ages separated by commas, e.g. 0, 2, 7",
                      html_for="existing_children_ages_group"),
            dbc.Input(
                id="existing_children_ages_input",
                placeholder="0, 2.5, 5",
                value="",
                type="text",
                debounce=True,
            ),
            dbc.FormFeedback(
                "The number of entries doesn't align with your prior response. Make sure you've used commas to separate your childrens' ages.",
                valid=False,
            ),
        ],
        id='existing_children_ages_group',
        className="mb-3",
        # invalid=None,
    )
)

n_future_children_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("How many *more* children do you plan on having in the future?",
                      html_for="n_future_children_group"),
            html.Div(
                dcc.Dropdown(
                    id='n_future_children_input',
                    options=[ {'label': n, 'value': n} for n in range(6) ],
                    value=0,
                    className="mb-3",
                ),
                className="dash-bootstrap"
            ),
        ],
        id='n_future_children_group',
        className="mb-3",
    )
)

next_child_age_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("When do you plan on having your next child?", html_for="next_child_age_group"),
            dbc.InputGroup(
                [
                    # dcc.Markdown(f"Within "),
                    dbc.InputGroupAddon("Within ", addon_type="prepend"),
                    dbc.Input(
                        id="next_child_max_years_input",
                        # placeholder=5,
                        type="number",
                        value=5,
                        min=0,
                        step=1,
                        debounce=True,
                    ),
                    dbc.InputGroupAddon(" year(s), but no sooner than ", addon_type="append"),
                    # dcc.Markdown(f" years, but no sooner than "),
                    dbc.Input(
                        id="next_child_min_years_input",
                        # placeholder=2,
                        type="number",
                        value=2,
                        min=0,
                        step=1,
                        debounce=True,
                    ),
                    dbc.InputGroupAddon(" year(s) from now.", addon_type="append"),
                    # dcc.Markdown(f" years from now."),
                ],
            ),
        ],
        id='next_child_age_group',
        className="mb-3",
    )
)

yrs_btwn_children_input = dbc.Col(
    dbc.FormGroup(
        [
            dbc.Label("We'll assume there'll be about 2 year(s) between the birth of your next child and each subsequent one, change that assumption here:",
                      html_for="yrs_btwn_children_group"),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Assuming ", addon_type="prepend"),
                    dbc.Input(
                        id="yrs_btwn_children_input",
                        # placeholder=2,
                        type="number",
                        value=2,
                        min=1,
                        step=1,
                        debounce=True,
                    ),
                    dbc.InputGroupAddon(" years between children. ", addon_type="append"),
                    # dcc.Markdown(f" years between children."),
                ],
            ),
        ],
        id='yrs_btwn_children_group',
        className="mb-3",
    )
)

"""
##  Graphs
"""
children_in_household_graph = dcc.Loading(
    id="loading-children-in-household",
    children=[dcc.Graph(id="forms-children-in-household-graph",
                        style={'display': 'none'})],
    type="default",
    style={'display': 'none'},
)

child_expenditures_graph = dcc.Loading(
    id="loading-child-expenditures",
    children=[dcc.Graph(id="forms-child-expenditures-graph",
                        style={'display': 'none'})],
    type="default",
    style={'display': 'none'},
)

relative_child_expenditures_graph = dcc.Loading(
    id="loading-relative-child-expenditures",
    children=[dcc.Graph(id="forms-relative-child-expenditures-graph",
                        style={'display': 'none'})],
    type="default",
    style={'display': 'none'},
)

"""
##  Overall Layout
"""
layout = dbc.Container(
    [
        html.H3("Cost of Raising Children Calculator"
                , style={'marginTop': 20, 'marginBottom': 20}
        ),
        dbc.Card(id='', children=
            [
                dbc.CardHeader('Personal Info'),
                dbc.CardBody(
                    [
                        dbc.Row(region_input),
                        dbc.Row(income_group_input),
                        dbc.Row(n_existing_children_input),
                        dbc.Row(existing_children_ages_input),
                        dbc.Row(n_future_children_input),
                        dbc.Row(next_child_age_input),
                        dbc.Row(yrs_btwn_children_input),
                        dbc.Card(dbc.CardBody(
                            dbc.Row(
                                dbc.Col(
                                    dcc.Tabs(
                                        id='tabs',
                                        children=[
                                            dcc.Tab(
                                                label="Children in Household",
                                                children=children_in_household_graph
                                                ),
                                            dcc.Tab(
                                                label="Total Expenditures",
                                                children=child_expenditures_graph
                                                ),
                                            dcc.Tab(
                                                label="Expenditure Breakdown",
                                                children=relative_child_expenditures_graph,
                                                ),
                                        ]
                                    )
                                )
                            )
                        ))
                        # children_in_household_graph,
                        # child_expenditures_graph,
                        # relative_child_expenditures_graph,
                    ]
                )
            ]
            , color="light"
            , style={'marginBottom': 20}
        ),
    ]
)

"""
## Helper Functions
"""
def get_existing_kids_bdays(age_str):
    ages = [float(x) for x in  age_str.split(',')]
    bdays = [pd.datetime.today().date() - pd.DateOffset(months=round(12 * x)) for x in ages]
    return bdays

def get_future_kids_bdays(n_future_kids, next_kid_min_yrs, next_kid_max_yrs, yrs_btwn_kids=2):
    next_kid_days_from_today = round(365*sum([next_kid_min_yrs, next_kid_max_yrs])/2)
    next_kid_date = pd.datetime.today().date() + pd.DateOffset(days=next_kid_days_from_today)
    future_bdays = [
        next_kid_date + pd.DateOffset(days=round(365*yrs_btwn_kids*x))
        for x in range(n_future_kids)
    ]
    return future_bdays

def get_bdays(kids_age_str, n_future_kids, next_kid_min_yrs, next_kid_max_yrs, yrs_btwn_kids):
    bdays = []
    if kids_age_str:
        bdays += get_existing_kids_bdays(kids_age_str)
    if n_future_kids > 0:
        future_bdays = get_future_kids_bdays(n_future_kids, next_kid_min_yrs,
                                             next_kid_max_yrs, yrs_btwn_kids)
        bdays += future_bdays

    return bdays

def get_n_kids_in_household(kids_bdays: List[pd.datetime],
                            years_in_household: int = 18
                           ) -> pd.Series:
    if len(kids_bdays) == 0:
        return pd.Series(
            data=0,
            index=pd.date_range(
                start=dt.today(),
                end=dt.today() + pd.DateOffset(years=10)
            ),
            name='n_kids_in_household'
        )

    date_ranges = [
        pd.Series(
            data=1,
            index=pd.date_range(
                start=x,
                end=x + pd.DateOffset(years=18),
                freq='d'
            ),
        )
        for x in sorted(kids_bdays)
    ]
    time_series = pd.concat(date_ranges, axis=1, join='outer').fillna(0).sum(axis=1)
    time_series.name = 'n_kids_in_household'
    time_series.loc[min(time_series.index) - pd.DateOffset(days=1)] = 0
    time_series.loc[max(time_series.index) + pd.DateOffset(days=1)] = 0
    time_series.sort_index(inplace=True)
    return time_series

def get_relevant_data(data, region, income_group):
    relevant_data = data.cleaned_data.get((region, income_group))
    return relevant_data / 365 # convert to daily basis

def create_age_series(bday):
    date_range = pd.date_range(
        start=bday,
        end=bday + pd.DateOffset(years=18),
        freq='d'
    )
    values = list(range(len(date_range)))
    return pd.Series(index=date_range, data=values, name='age_in_days')

def create_expenditure_series(bday, relevant_data):
    age_series = create_age_series(bday)
    return (
        age_series
        .reset_index()
        .merge(
            relevant_data,
            left_on='age_in_days',
            right_index=True,
            how='outer'
        ).fillna(method='ffill')
        .set_index('index')
        .drop(columns=['age_in_days'])
        .resample('M')
        .sum()
    )

def combine_expenditures(expenditures):
    def fn(df1, df2):
        return df1.add(df2, fill_value=0)
    return reduce(fn, expenditures)

def get_n_kids_multiplier(n_kids):
    if n_kids == 1:
        return 1.27
    elif n_kids == 2:
        return 1
    elif n_kids >= 3:
        return 0.76
    else:
        return 0

def get_n_kids_fig(n_kids_ts):
    fig = px.line(n_kids_ts,
                  x=n_kids_ts.index,
                  y='n_kids_in_household',
                  title="Number of children in household through time",
                  range_y=(0, n_kids_ts.max() + 2),
                  range_x=(
                    n_kids_ts.index.min() - pd.DateOffset(months=3),
                    n_kids_ts.index.max() + pd.DateOffset(months=3)
                    )
                    )
    fig.update_yaxes(title='Number of children in household')
    fig.update_xaxes(title='')

    return fig

def clean_exp_col_name(x):
    return x.split('_exp')[0].replace('_', ' ').capitalize()

def get_expenditures_fig(expenditures):

    col_renaming_map = {x: clean_exp_col_name(x) for x in expenditures.columns}
    expenditures.rename(columns=col_renaming_map, inplace=True)

    to_plt = (
        expenditures
        .resample('Y')
        .sum()
        .stack()
        .reset_index()
        .rename(columns={
            'index': 'Date',
            'level_1': 'Expense Category',
            0: 'Amount'
        })
    )
    to_plt['Amount'] = to_plt['Amount'].apply(lambda x: round(x, 0))

    total_exp = to_plt[to_plt['Expense Category'] == 'Total']

    fig_abs = px.area(to_plt[to_plt['Expense Category'] != 'Total'], x='Date',
                      y='Amount', color='Expense Category')
    fig_abs.add_scatter(x=total_exp['Date'], y=total_exp['Amount'], name='Total',
                        mode='lines+markers', line_color="rgb(29, 105, 150)")
    fig_abs.update_yaxes(title='Child Expenditure Per Year', tickformat="$,.0", )
    fig_abs.update_xaxes(title='')
    fig_abs.update_layout(legend={'orientation':'h'})

    fig_rel = px.area(to_plt[to_plt['Expense Category'] != 'Total'], x='Date',
                      y='Amount', color='Expense Category', groupnorm='fraction')
    fig_rel.update_yaxes(title='Proportion of Child Expenditures',
                         tickformat="%", range=[0, 1])
    fig_rel.update_xaxes(title='')
    fig_rel.update_layout(legend={'orientation':'h'})

    return fig_abs, fig_rel

"""
#  Callbacks
"""
@app.callback(
    [
        Output(component_id='forms-children-in-household-graph', component_property='figure'),
        Output(component_id='forms-children-in-household-graph', component_property='style'),
        Output(component_id='loading-children-in-household', component_property='style'),
        Output(component_id='forms-child-expenditures-graph', component_property='figure'),
        Output(component_id='forms-child-expenditures-graph', component_property='style'),
        Output(component_id='loading-child-expenditures', component_property='style'),
        Output(component_id='forms-relative-child-expenditures-graph', component_property='figure'),
        Output(component_id='forms-relative-child-expenditures-graph', component_property='style'),
        Output(component_id='loading-relative-child-expenditures', component_property='style'),
    ],
    [
        Input('existing_children_ages_input', 'value'),
        Input('n_future_children_input', 'value'),
        Input('next_child_min_years_input', 'value'),
        Input('next_child_max_years_input', 'value'),
        Input('yrs_btwn_children_input', 'value'),
        Input('region_input', 'value'),
        Input('income_group_input', 'value'),
    ],
)
def update_children_in_household(kids_age_str: str,
                                 n_future_kids: int,
                                 next_kid_min_yrs: float,
                                 next_kid_max_yrs: float,
                                 yrs_btwn_kids: float,
                                 geo: str,
                                 income_group: str,
                                 ):
    bdays = get_bdays(
        kids_age_str=kids_age_str,
        n_future_kids=n_future_kids,
        next_kid_min_yrs=next_kid_min_yrs,
        next_kid_max_yrs=next_kid_max_yrs,
        yrs_btwn_kids=yrs_btwn_kids,
        )

    n_kids_ts = get_n_kids_in_household(kids_bdays=bdays)
    n_kids_fig = get_n_kids_fig(n_kids_ts)
    # n_kids_fig = go.Figure()

    if len(bdays) > 0:
        relevant_data = get_relevant_data(DATA, geo, income_group)
        expenditure_series = [create_expenditure_series(x, relevant_data) for x in bdays]
        total_expenditures = combine_expenditures(expenditure_series)
        # print(total_expenditures.head(5))
        n_kids_multiplier = (
            n_kids_ts
            .apply(get_n_kids_multiplier) # Take into account economies of scale w/ multiple kids
            .reindex(total_expenditures.index)
            )
        # print(n_kids_multiplier.head())
        total_expenditures = total_expenditures.multiply(n_kids_multiplier, axis=0)
        # print(total_expenditures.head())

        exp_fig, rel_exp_fig = get_expenditures_fig(total_expenditures)
        for_title = f"Married Couple in {geo} w/ Income {income_group} and {len(bdays)} Children"
        exp_fig.update_layout(title="Child Expenditures - " + for_title)
        rel_exp_fig.update_layout(title="Child Expenses Breakdown - " + for_title)

    else:
        exp_fig = go.Figure()
        rel_exp_fig = go.Figure()

    display = {'display': 'block'} if len(bdays) > 0 else {'display': 'none'}

    return n_kids_fig, display, display, exp_fig, display, display, rel_exp_fig, display, display

@app.callback(
    [
        Output(component_id='existing_children_ages_group', component_property='style'),
        Output(component_id='existing_children_ages_input', component_property='value'),
    ],
    [
        Input('n_existing_children_input', 'value'),
    ],
    [
        State('existing_children_ages_input', 'value')
    ]
)
def toggle_container(n_existing_children, kids_age_str):
    if n_existing_children == 0:
        return {'display': 'none'}, ""
    else:
        return {'display': 'block'}, kids_age_str

@app.callback(
    Output("existing_children_ages_input", "invalid"),
    [
        Input('n_existing_children_input', 'value'),
        Input('existing_children_ages_input', 'value')
    ]
)
def validate(n_existing_children, kids_age_str):
    valid = kids_age_str.count(',') == n_existing_children - 1
    return not valid

@app.callback(
    Output(component_id='next_child_age_group', component_property='style'),
    [Input('n_future_children_input', 'value')]
)
def toggle_container(n_future_children):
    if n_future_children == 0:
        return {'display': 'none'}
    else:
        return {'display': 'block'}

@app.callback(
    Output(component_id='yrs_btwn_children_group', component_property='style'),
    [Input('n_future_children_input', 'value')]
)
def toggle_container(n_future_children):
    if n_future_children < 2:
        return {'display': 'none'}
    else:
        return {'display': 'block'}
