# I'll try to make the interactive chlorplet map here
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from src.data_preprocessing.preprocessing import load_data, get_ISO3, clean_country_names, merge_data
from dash_bootstrap_templates import load_figure_template

load_figure_template("darkly")

def generate_choropleth() -> go.Figure:

    df = load_data()
    df = merge_data(df)
    df = clean_country_names(df)

    cols_to_ignore = ["Country", "ISO3"]  
    mask = df.drop(columns=cols_to_ignore).isna().all(axis=1)
    
    only_nas = df[mask]
    
    fig = go.Figure(go.Choropleth(
        locations=df["ISO3"],
        z=[1] * len(df),  # dummy value so Plotly draws the shapes
        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],  # fully transparent fill
        showscale=False,
        hovertext=df["Country"],
        hoverinfo="text",
        marker_line_color="#8cdba9",   # border color
        marker_line_width=0.8,
    ))

    fig.update_geos(
        projection_type="natural earth",
        fitbounds="locations",
        visible=False,
        showland=True,
        landcolor="#151a22",   # dark land
    )
    

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#111111",  # outer background
        geo_bgcolor="#111111"
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






