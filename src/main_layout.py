import pandas as pd
import numpy as np
import plotly.express as px
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import plotly.io as pio
from dash import Dash, html, dcc, Input, Output, State, clientside_callback, callback, Patch
from src.pages.map import generate_choropleth
from dash_bootstrap_templates import load_figure_template
from src.pages.tabs import tab_layout
from src.data_preprocessing.preprocessing import load_data, get_ISO3, clean_country_names, merge_data

load_figure_template("darkly")

def get_layout():
    fig = generate_choropleth()
    data_dict = load_data()
    df = merge_data(data_dict)
    df = clean_country_names(df)

    #df = [{'label': country, 'value': iso3} for country, iso3 in zip(df['Country'], df['ISO3'])]
    return dbc.Container(
        [
            dbc.Row([
                dbc.Col(html.H1("Main Layout", className="text-center text-primary mb-4"), width=12),
                dbc.Col(dcc.Graph(
                    id="graph",
                    figure=fig,
                    className="dbc"
                ),
                width=12,
                className="mb-4"
                ),
                dbc.Col(
                    width=8,
                    className="mt-4",
                    children=[
                        tab_layout()
                    ]
                ),
                dbc.Col(
                    width=4,
                    className="mt-4",
                    children=[
                        dcc.Dropdown(
                            id="country-dropdown",
                            options = df.Country.unique(),
                            className="dbc"
                        )
                    ]
                )
            ]),

        ]
    )

    
@callback(
    Output(component_id="graph", component_property="figure"),
    Input(component_id="views-radioitems", component_property="value")
)
def update_graph(selected_column):
    df = load_data()
    df = merge_data(df)
    df = clean_country_names(df)

    cols_to_ignore = ["Country", "ISO3"]  
    mask = df.drop(columns=cols_to_ignore).isna().all(axis=1)
    only_nas = df[mask]

    
    fig =px.choropleth(
        df,
        locations="ISO3",
        color=selected_column,
        hover_name="Country",
        color_continuous_scale=px.colors.sequential.Plasma,
        title=f"Choropleth Map of {selected_column.replace('_', ' ')}"
    )
    fig.update_geos(
        projection_type="natural earth",
        fitbounds="locations",
        visible=False,
        showland=True
    )
    fig.add_choropleth(
        locations = only_nas["ISO3"],
        z = [1] * len(df),
        #colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],  # fully transparent fill
        showscale=False,
        hovertext = "No data available for " + only_nas["Country"],
        hoverinfo="text",
        marker_line_color="#E4CFCF",   # border color
        marker_line_width=0.8,
    )
    return fig
