import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as sp

from gameplan.growth.income_percentile_estimate import get_working_population_data

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

layout = html.Div(children=[
    html.H3('Salary Calculator'),
    html.Div(children=[
        'Metro Area (DMA):',
        dcc.Dropdown(
            id='dma',
            options=[{'label': dma, 'value': dma} for dma in DMAS],
            value='New York-Northern New Jersey-Long Island, NY-NJ-PA'
        )]),
    html.Div(children=[
        'Total Annual Income: $',
        dcc.Input(id='annual_income', type='number', value=30000)
        ]),
    html.Div(children=[
        'Your Age: ',
        dcc.Input(id='age_input', type='number', value=25),
        html.Div(children=[
            'Relevant Age Range for Cohort: ',
            # dcc.Input(id='age_bucket_left', type='number', value=23),
            # dcc.Input(id='age_bucket_right', type='number', value=27),
            dcc.RangeSlider(
                id='age_range',
                count=1,
                min=22,
                max=65,
                step=1,
                value=[23, 27],
                # marks=
                tooltip={'always_visible': True, 'placement': 'bottom'}
            )]),
        ]),
    html.Div(children=[
        'Gender: ',
        dcc.RadioItems(
            id='gender',
            options=[
                {'label': 'Female', 'value': 'Female'},
                {'label': 'Male', 'value': 'Male'},
                {'label': 'Prefer Not To Say', 'value': 'Neither'}
            ],
            value='Male',
            labelStyle={'display': 'inline-block'}
        )
        ]),
    dcc.Graph(id='output-graph'),
])

@app.callback(
    Output('age_range', 'value'),
    [Input('age_input', 'value')]
    )
def set_age_buckets(age_input):
    return [age_input - 2, age_input + 2]

def construct_query(dma, age_range, gender):
    if gender == 'Neither':
        gender_clause = "(sex == 'Male' | sex == 'Female')"
    else:
        gender_clause = f"sex == '{gender}'"
    query = f" \
        metarea.str.contains(@dma) \
        & AGE.between(@age_range[0], @age_range[1]) \
        & {gender_clause} \
        "
    return query

def get_fig(df, salary, dma, age_range, gender):
    query = construct_query(dma, age_range, gender)
    subset = df.query(query)
    subset['weight'] = subset.ASECWT / subset.ASECWT.sum()
    dist = subset.sort_values('inctot').loc[:, ['inctot', 'weight']]
    dist['cdf'] = dist.weight.cumsum()
    fig = px.line(
        dist,
        x='inctot',
        y='cdf',
        range_x=(0, 250000),
        range_y=(0,1)
        )
    percentile = sp.percentileofscore(dist.inctot, int(salary))
    fig.add_scatter(
        x=[salary, salary],
        y=[0, 1],
        mode='lines',
        line=dict(color='black', width=2, dash='dot'),
        showlegend=False
    )
    fig.add_annotation(
        text=f'${salary:,} = {percentile:.0f}th Percentile',
        x=salary,
        y=percentile/100,
        showarrow=True,
        align='left',
        font=dict(size=14)
        )
    gender_clause = '' if gender == 'Neither' else f" {gender.lower()}"
    title = (
        f"Total income distribution among full-time{gender_clause} workers, "
        f"aged {age_range[0]} to {age_range[1]}, "
        f"living in {dma}"
    )
    layout = go.Layout(
        title=title,
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
        text=f'Sample includes {len(subset):,.0f} individuals.',
        x=1,
        y=-0.1,
        xref='paper', yref='paper',
        xanchor='right', yanchor='auto', xshift=0, yshift=0,
    )

    return fig


@app.callback(
    Output(component_id='output-graph', component_property='figure'),
    [
        Input(component_id='dma', component_property='value'),
        Input('annual_income', 'value'),
        Input('age_range', 'value'),
        Input('gender', 'value'),
    ],
)
def update_figure(dma, salary, age_range, gender):
    fig = get_fig(
        df=working_pop,
        dma=dma,
        salary=salary,
        age_range=age_range,
        gender=gender
        )
    return fig

# if __name__ == '__main__':
#     app.run_server(debug=True)
