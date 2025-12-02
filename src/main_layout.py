import pandas as pd
import numpy as np
import plotly.express as px
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import plotly.io as pio
from dash import Dash, html, dcc, Input, Output, State, clientside_callback, callback, Patch
from src.pages.map import generate_choropleth, make_base_map
from dash_bootstrap_templates import load_figure_template
from src.pages.tabs import tab_layout
from src.data_preprocessing.preprocessing import load_data, get_ISO3, clean_country_names, merge_data

load_figure_template("darkly")

df = clean_country_names(merge_data(load_data()))
cols_to_ignore = ["Country", "ISO3"]
mask_empty = df.drop(columns=cols_to_ignore).isna().all(axis=1)
df_empty = df[mask_empty]
df_nonempty = df[~mask_empty]

fig_map = generate_choropleth()

def get_layout():
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
                    figure=fig_map,
                    className="dbc",
                    #animate=True
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


""" @callback(
    Output(component_id="graph", component_property="figure", allow_duplicate=True),
    Input(component_id="country-dropdown", component_property="value"),
    prevent_initial_call=True
)

def zoom_country(selected_country):
    if selected_country is None:
        return fig_map
    
    fig_map.update_geos(
        center = dict(lat = df.loc[df['Country'] == selected_country, 'Latitude'].values[0], lon = df.loc[df['Country'] == selected_country, 'Longitude'].values[0]),
        projection_scale = 3.0,
        fitbounds = None
    )  """  


    
@callback(
    Output(component_id="graph", component_property="figure"),
    Input(component_id="views-radioitems", component_property="value"),
)
def update_graph(selected_column):


    if selected_column == None:
        print("No column selected.")
        return fig_map
    elif selected_column not in df.columns:
        print("Selected column not found in DataFrame.")
        return fig_map

    fig = make_base_map()

    fig.add_choropleth(
        locations=df_nonempty["ISO3"],
        z = df_nonempty[selected_column],
        colorscale= px.colors.sequential.Plasma,
        hovertext= df_nonempty["Country"],
        hoverinfo="text+z",
    )

    mask_empty_col = df_nonempty[selected_column].isna()
    df_empty_col = df_nonempty[mask_empty_col]
    df_empty_col = pd.concat([df_empty, df_empty_col], ignore_index=True)

    fig.add_choropleth(
        locations = df_empty_col["ISO3"],
        z = [0] * len(df_empty_col),
        showscale=False,
        hovertext = "No data available",
        hoverinfo="text",
        marker_line_color="#E4CFCF",
        marker_line_width=0.8,
        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
    )

    fig.update_traces(marker_line_color="#8cdba9", selector=dict(type='choropleth', showscale=True))
    fig.update_layout(title=f"{selected_column.replace('_', ' ').title()} by Country")

    return fig
