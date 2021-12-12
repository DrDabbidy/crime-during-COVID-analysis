"""Generate a heatmap given p-index data."""

import plotly.express as px
import pandas as pd
import json
from crime_data import CrimeData
import dash
from dash import dcc
from dash import html


def generate_heatmap(data: CrimeData) -> None:
    """Generate an animated heatmap for the pindexes of the crime over time given the CrimeData,
    data."""
    # open the geojson file of the neighbourhood boundaries
    with open('local-area-boundary.geojson') as file:
        regions = json.load(file)

    # Create a pandas dataframe with all the necessary data
    unpacked_data = unpack_data(data)
    df = pd.DataFrame({'date': unpacked_data[0],
                       'region': unpacked_data[1],
                       'p-index': unpacked_data[2],
                       'crime-type': unpacked_data[3]})

    crime_types = list(data.crime_pindex.keys())

    # Create a dash app with a dropdown menu so that we can switch between graphs
    app = dash.Dash()
    app.layout = html.Div([
        dcc.Dropdown(
            id='crime-type-dropdown',
            options=[{'label': crime, 'value': crime} for crime in crime_types],
            value=crime_types[0]
        ),
        dcc.Graph(id='choropleth-graph')])

    # this function is called every time the dropdown menu is updated.
    @app.callback(
        dash.dependencies.Output('choropleth-graph', 'figure'),
        [dash.dependencies.Input('crime-type-dropdown', 'value')])
    def update_output(crime: str):
        """Updates which graph is shown in our app."""
        fig = px.choropleth_mapbox(df[df['crime-type'] == crime], geojson=regions,
                                   locations='region',
                                   color='p-index',
                                   color_continuous_scale=['LawnGreen', 'LightBlue', 'DarkRed'],
                                   range_color=(-100, 100),
                                   featureidkey="properties.name",
                                   mapbox_style="carto-positron",
                                   opacity=0.5,
                                   center={"lat": 49.24200376111951, "lon": -123.13312355113719},
                                   zoom=11,
                                   animation_frame='date',
                                   height=750)

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(title=f'<b>P-index graph for {crime}</b>')
        return fig

    app.run_server()


def unpack_data(data: CrimeData) -> tuple[list[str], list[str], list[float], list[str]]:
    """Unpack the data in CrimeData into three lists, one corresponding to the dates, one to the
    regions, and one to the pindexes."""
    dates = []
    regions = []
    pindexes = []
    crime_types = []

    for crime in data.crime_pindex:
        for obj in data.crime_pindex[crime].values():
            years = sorted(list(obj.p_index_dict.keys()))
            for year in years:
                months = list(obj.p_index_dict[year].keys())
                # print(months)
                for month in months:
                    dates.append(month_year_to_str(month, year))
                    regions.append(obj.neighbourhood)
                    pindexes.append(obj.get_data(year, month))
                    crime_types.append(crime)

    return dates, regions, pindexes, crime_types


def month_year_to_str(month: int, year: int) -> str:
    """Given the month and year as ints, return the datestring in the form 'month year'"""

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return f'{months[month - 1]} {year}'