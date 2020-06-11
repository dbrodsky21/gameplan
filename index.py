import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from apps import child_expenditures, salary_calculator, income_forecast, forms


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    # if pathname == '/apps/salary-calculator':
    #     return salary_calculator.layout
    if pathname == '/apps/income-forecast':
        return income_forecast.layout
    if pathname == '/apps/forms':
        return forms.layout
    # if pathname == '/apps/child-expenditures':
    #     return child_expenditures.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)
