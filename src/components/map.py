# I'll try to make the interactive chlorplet map here
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from src.data_loading.load_data import load_data_into_df
from src.components.filter import get_label
from dash_bootstrap_templates import load_figure_template

load_figure_template("darkly")

def generate_choropleth() -> go.Figure:

    df = load_data_into_df()

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
        hovertext = "No data available for " + only_nas["Country"] + " " + only_nas["ISO3"],
        hoverinfo="text",
        marker_line_color="#E4CFCF",   # border color
        marker_line_width=0.8,
    )

    fig.update_layout(
    coloraxis_showscale=False,
    coloraxis=None
    )

    for trace in fig.data:
        if hasattr(trace, 'coloraxis'):
            trace.coloraxis = None

    """ fig.update_layout(
        transition=dict(duration=100, easing="cubic-in-out")
    ) """

    return fig


def build_hover_text(row: pd.Series, active_filters: dict) -> str:
    country = [row["Country"]]

    for col_name, val in active_filters.items():
        if col_name in row.index and pd.notna(row[col_name]):
            label = get_label(col_name)
            country.append(f"<br>{label}: {row[col_name]}")

    return "<br>".join(country)


def generate_filter_based_chloropeth(df:pd.DataFrame, active_filters: dict, missing_by_filter: dict, only_nas):

    df = df.copy()

    globally_empty_iso3 = set(only_nas["ISO3"].tolist())


    if df.empty:
        return generate_choropleth()

    df["hover_text"] = df.apply(
        lambda row: build_hover_text(row, active_filters), axis = 1
    )

    
    

    all_missing_iso3 = set()
    for _, missing_set in missing_by_filter.items():
        all_missing_iso3.update(missing_set)

    fig = go.Figure(go.Choropleth(
        locations=df["ISO3"],
        z=[1] * len(df),  # dummy value so Plotly draws the shapes
        colorscale=[[0, "lime"], [1, "lime"]],  # fully transparent fill
        showscale=False,
        hovertext=df["hover_text"],
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
        z = [1] * len(only_nas),
        #colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],  # fully transparent fill
        showscale=False,
        hovertext = "No data available for " + only_nas["Country"] + " globally",
        hoverinfo="text",
        marker_line_color="#E4CFCF",   # border color
        marker_line_width=0.8,
    )

    for filter_name, missing_set in missing_by_filter.items():

        missing_set_filtered = missing_set - globally_empty_iso3

        if missing_set_filtered:  # Only add layer if there are countries to show
            fig.add_choropleth(
                locations=list(missing_set_filtered),
                z=[1] * len(missing_set_filtered),
                colorscale=[[0, "#FFD700"], [1, "#FFD700"]],  # Gold for filter-excluded
                showscale=False,
                hovertext=[f"Missing data for {get_label(filter_name)}" for _ in missing_set_filtered],
                hoverinfo="text",
                marker_line_color="#8cdba9",
            )


    return fig


def make_base_map() -> go.Figure:
    fig = go.Figure()
    fig.update_geos(
        projection_type="natural earth",
        fitbounds="locations",
        visible=False,
        showland=True,
        landcolor="#151a22",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#111111",
        geo_bgcolor="#111111",
    )
    return fig




