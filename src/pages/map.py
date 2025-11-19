# I'll try to make the interactive chlorplet map here
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from src.data_preprocessing.preprocessing import load_data, get_ISO3, clean_country_names, merge_data
from dash_bootstrap_templates import load_figure_template

load_figure_template("darkly")

def generate_choropleth():

    df = load_data()
    df = merge_data(df)
    df = clean_country_names(df)
    
    
    fig = go.Figure(go.Choropleth(
        locations=df["ISO3"],
        z=[1] * len(df),  # dummy value so Plotly draws the shapes
        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],  # fully transparent fill
        showscale=False,
        hovertext=df["Country"],
        hoverinfo="text",
        marker_line_color="#888888",   # border color
        marker_line_width=0.4,
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

    return fig





