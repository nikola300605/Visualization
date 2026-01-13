import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output

from src.components.map import generate_choropleth, make_base_map
from src.components.tabs import tab_layout
from src.data_loading.load_data import load_data_into_df

dash.register_page(__name__, path="/", name="Home", order=0)

df = load_data_into_df()
cols_to_ignore = ["Country", "ISO3"]
mask_empty = df.drop(columns=cols_to_ignore).isna().all(axis=1)
df_empty = df[mask_empty]
df_nonempty = df[~mask_empty]

fig_map = generate_choropleth()

layout = dbc.Container(
    dbc.Row([
        dbc.Col(dcc.Graph(id="graph", figure=fig_map, className="dbc"),
                width=12, className="mb-4"),

        dbc.Col(tab_layout(), width=12, className="mt-4"),
    ]),
    fluid=True
)

@callback(Output("graph", "figure"), Input("views-radioitems", "value"))
def update_graph(selected_column):
    if selected_column is None or selected_column not in df.columns:
        return fig_map

    fig = make_base_map()
    fig.add_choropleth(
        locations=df_nonempty["ISO3"],
        z=df_nonempty[selected_column],
        colorscale=px.colors.sequential.Plasma,
        hovertext=df_nonempty["Country"],
        hoverinfo="text+z",
    )

    mask_empty_col = df_nonempty[selected_column].isna()
    df_empty_col = pd.concat([df_empty, df_nonempty[mask_empty_col]], ignore_index=True)

    fig.add_choropleth(
        locations=df_empty_col["ISO3"],
        z=[0] * len(df_empty_col),
        showscale=False,
        hovertext="No data available",
        hoverinfo="text",
        marker_line_width=0.8,
        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
    )

    fig.update_layout(title=f"{selected_column.replace('_', ' ').title()} by Country")
    return fig


""" @Callback(
    Output("graph", "figure"),
    Input("")
) """