import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import pandas as pd
import scipy.stats as sp

from gameplan.growth.income_percentile_estimate import get_working_population_data
from gameplan.growth.growth_models import KitcesIncomeGrowthModel
from gameplan.user import User
from gameplan.income_streams import Salary

from app import app

working_pop = get_working_population_data()
DMAS = [
    'New York-Northern New Jersey-Long Island, NY-NJ-PA',
    'Los Angeles-Long Beach-Anaheim, CA',
    'Washington, DC/MD/VA',
    'Chicago-Naperville-Joliet, IL-IN-WI',
    'Boston-Cambridge-Newton, MA-NH',
    'Dallas-Fort Worth-Arlington, TX',
    'Philadelphia-Camden-Wilmington, PA/NJ/DE',
]


"""
#  Layout
"""

NAVBAR = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    # dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(
                        dbc.NavbarBrand("Bank Customer Complaints", className="ml-2")
                    ),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://plot.ly",
        )
    ],
    color="dark",
    dark=True,
    sticky="top",
)

LEFT_COLUMN = dbc.Jumbotron(
    [
        html.H4(children="Define your comparison cohort", className="display-5", style={"font-size": 24, "marginTop": 0}),
        html.Hr(className="my-2"),
        html.Label("Select your Metro Area (DMA)", style={"marginTop": 10, "font-size": 20}, className="lead"),
        dcc.Dropdown(
            id='dma',
            options=[{'label': dma, 'value': dma} for dma in DMAS],
            value='New York-Northern New Jersey-Long Island, NY-NJ-PA',
            clearable=False,
            style={"marginBottom": 0, "font-size": 12},
        ),
        html.Div(children=[
            html.Label("Enter your total annual income: ", style={"marginTop": 10}, className="lead"),
            dcc.Input(
                id='annual_income',
                type='number',
                value=30000,
                style={"marginBottom": 5, "font-size": 14},
                ),
        ]),
        html.Div(children=[
            html.Label("Enter your Age:", style={"marginTop": 10}, className="lead"),
            dcc.Input(id='age_input', type='number', value=25),
            ]),
        html.Div(children=[
            'Adjust relevant age range for your cohort: ',
            dcc.RangeSlider(
                id='age_range',
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
            )], style={"marginTop": 10, "font-size": 16}
            ),
        html.Div(children=[
            'Select genders to include in your cohort: ',
            dbc.RadioItems(
                id='gender',
                options=[
                    {'label': 'Female', 'value': 'Female'},
                    {'label': 'Male', 'value': 'Male'},
                    {'label': 'All', 'value': 'All'}
                ],
                value='All',
                inline=True
                # labelStyle={'display': 'inline-block'}
            )
            ]),
    ]
)

INCOME_PLOTS = [
    dbc.CardHeader(id='income-charts-header'),
    dbc.Alert(
        "Not enough data to render these plots, please adjust the filters",
        id="no-data-alert",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Tabs(
                                id="tabs",
                                children=[
                                    dcc.Tab(
                                        label="Income Distribution",
                                        children=[
                                            dcc.Loading(
                                                id="loading-income-dist",
                                                children=[dcc.Graph(id="income-dist-graph")],
                                                type="default",
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="Income Trajectory",
                                        children=[
                                            dcc.Loading(
                                                id="loading-income-trajectory",
                                                children=[
                                                    dcc.Graph(id="income-trajectory-graph")
                                                ],
                                                type="default",
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                        md=0,
                    ),
                ]
            )
        ]
    ),
]

BODY = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(LEFT_COLUMN, md=4, align="center"),
                dbc.Col(dbc.Card(INCOME_PLOTS), md=0),
            ],
            style={"marginTop": 30},
        ),
    ],
    className="mt-12",
)

layout = html.Div(children=[BODY])

"""
# Helper functions
"""
def get_percentile_label(x):
    pctile = round(x) # sp.percentile returns percentiles out of 100, not 1
    last_digit = str(pctile)[-1]
    suffix_dict = {
        '1' : 'st',
        '2' : 'nd',
        '3' : 'rd'
    }

    return f"{pctile}{suffix_dict.get(last_digit, 'th')}"

def construct_subset_query(dma, age_range, gender):
    if gender in ['Male', 'Female']:
        gender_clause = f"sex == '{gender}'"
    else:
        gender_clause = "(sex == 'Male' | sex == 'Female')"
    query = f" \
        metarea.str.contains(@dma) \
        & AGE.between(@age_range[0], @age_range[1]) \
        & {gender_clause} \
        "
    return query

def get_cohort_subset(df, dma, age_range, gender) -> pd.DataFrame:
    query = construct_subset_query(dma, age_range, gender)
    return df.query(query)

def get_cdf(df):
    df['weight'] = df.ASECWT / df.ASECWT.sum()
    dist = df.sort_values('inctot').loc[:, ['inctot', 'weight']]
    dist['cdf'] = dist.weight.cumsum()
    return dist

def get_income_percentile(salary, inc_dist):
    pass

def get_income_dist_fig(df, salary, dma, age_range, gender, return_pctile=True):
    subset = get_cohort_subset(df, dma, age_range, gender)
    dist = get_cdf(subset)
    percentile = sp.percentileofscore(dist.inctot, int(salary))

    fig = px.line(
        dist,
        x='inctot',
        y='cdf',
        range_x=(0, 250000),
        range_y=(0,1)
        )
    fig.add_scatter(
        x=[salary, salary],
        y=[0, 1],
        mode='lines',
        line=dict(color='black', width=2, dash='dot'),
        showlegend=False
    )
    fig.add_annotation(
        text=f'${salary:,} = {get_percentile_label(percentile)} Percentile',
        x=salary,
        y=percentile/100,
        xref='x',
        yref='y',
        showarrow=True,
        # align='center',
        font=dict(size=14),
        xanchor='left',
        # yanchor='top',
        # yshift=-20,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        ax=50,
        ay=-40
        # ay=-30,
        )

    gender_clause = f" {gender.lower()}" if gender in ['Male', 'Female']  else ''
    title = (
        f"Total income distribution among full-time{gender_clause} workers, "
        f"aged {age_range[0]} to {age_range[1]}, "
        f"living in: <br>{dma} <br>"
    )
    layout = go.Layout(
        title=go.layout.Title(text=title, xanchor='center', x=0.5),
        yaxis={
            "title": "% of Full-Time Workers Earning Up To $X Per Year",
            "range": [0, 1],
            },
        xaxis={"title": "Total Annual Income"},
        font=dict(
            # family="Courier New, monospace",
            size=10,
            # color="#7f7f7f"
        )
        )
    fig.update_layout(layout)
    fig.add_annotation(
        showarrow=False,
        text=f'Cohort sample includes {len(subset):,.0f} individuals.',
        x=1,
        y=-0.1,
        xref='paper', yref='paper',
        xanchor='right', yanchor='auto', xshift=0, yshift=0,
    )

    to_return = fig, percentile if return_pctile else fig
    return to_return

def get_pctile_for_growth(x):
    "Current growth model only has 0, 10 ... 90th percentiles"
    if x == 100:
        x -= 1
    return np.floor(x/10)*10

def get_salary_trajectory(pctile_for_growth, age, current_salary):
    user = User(
        email='placeholder',
        birthday=pd.datetime.today() - pd.DateOffset(years=age),
        income_percentile=pctile_for_growth
        )

    sal_grwth_points = user.get_growth_points_to_fit(
        growth_model=KitcesIncomeGrowthModel,
        start_dt=pd.datetime.today()
    )
    s = Salary(
        current_salary,
        payday_freq='Y',
        growth_points_to_fit=sal_grwth_points,
        last_paycheck_dt= pd.datetime.today() + pd.DateOffset(years=65 - age),
        tax_rate=.35
    )
    return s

def get_growth_scenarios(percentile, age, current_salary):
    pctile_for_growth = get_pctile_for_growth(percentile)
    growth_scenarios = {
        'Optimistic': {'grwth_pctile': pctile_for_growth + 10},
        'Status Quo': {'grwth_pctile': pctile_for_growth},
        'Pessimistic': {'grwth_pctile': pctile_for_growth - 10},
    }
    # We don't have an "optimistic" scenario if you're in the 90th pctile
    if pctile_for_growth >= 90:
        growth_scenarios.pop('Optimistic')
    elif pctile_for_growth <= 10:
        growth_scenarios.pop('Pessimistic')

    for scn, v in growth_scenarios.items():
        v['sal_traj'] = get_salary_trajectory(v['grwth_pctile'], age, current_salary)

    return growth_scenarios


def get_income_trajectory_fig(df, salary, dma, age_range, gender, age):
    subset = get_cohort_subset(df, dma, age_range, gender)
    dist = get_cdf(subset)
    percentile = sp.percentileofscore(dist.inctot, int(salary))
    growth_scenarios = get_growth_scenarios(percentile, age, salary)
    bday = pd.datetime.today() - pd.DateOffset(years=age)
    data = [
        go.Scatter(
            x=[
                round((dt-bday).days/365) # creating an age index
                for dt in v['sal_traj'].paycheck_df.index
               ],
            y=v['sal_traj'].paycheck_df.salary,
            name=f"{scn} Growth Trajectory - {int(v['grwth_pctile'])}th percentile",
            mode='markers+lines'
        )
        for scn, v in growth_scenarios.items()
    ]

    layout = go.Layout(
        title=go.layout.Title(
            text='Income Growth Scenarios (inflation adjusted)',
            xanchor='center',
            x=0.5
        ),
        xaxis=go.layout.XAxis(
            title='Age',
            dtick=5,
        ),
        yaxis=go.layout.YAxis(
            title='Pre-Tax Income in 2019 Dollars (inflation-adjusted)'
        ),
        legend=go.layout.Legend(orientation='h', y=-0.2),
    )

    return go.Figure(data, layout)

"""
#  Callbacks
"""
@app.callback(
    Output('age_range', 'value'),
    [Input('age_input', 'value')]
    )
def set_age_buckets(age_input):
    return [age_input - 2, age_input + 2]

@app.callback(
    [
        Output(component_id='income-dist-graph', component_property='figure'),
        Output(component_id='income-charts-header', component_property='children')
    ],
    [
        Input(component_id='dma', component_property='value'),
        Input('annual_income', 'value'),
        Input('age_range', 'value'),
        Input('gender', 'value'),
    ],
)
def update_income_dist_figure(dma, salary, age_range, gender):
    fig, percentile = get_income_dist_fig(
        df=working_pop,
        dma=dma,
        salary=salary,
        age_range=age_range,
        gender=gender,
        return_pctile=True
        )
    percentile_label = f"Within your cohort you fall into the {get_percentile_label(percentile)} percentile"
    return fig, percentile_label


@app.callback(
    Output(component_id='income-trajectory-graph', component_property='figure'),
    [
        Input(component_id='dma', component_property='value'),
        Input('annual_income', 'value'),
        Input('age_range', 'value'),
        Input('gender', 'value'),
        Input('age_input', 'value'),

    ],
)
def update_income_trajectory_figure(dma, salary, age_range, gender, age):
    fig = get_income_trajectory_fig(
        df=working_pop,
        dma=dma,
        salary=salary,
        age_range=age_range,
        gender=gender,
        age=age
        )
    return fig
