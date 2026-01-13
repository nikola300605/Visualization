import pandas as pd
import numpy as np
import plotly.express as px
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import plotly.io as pio
from dash import Dash, html, dcc, Input, Output, State, clientside_callback, callback, Patch
from src.pages.map import generate_choropleth
from dash_bootstrap_templates import load_figure_template

load_figure_template("darkly")


def get_layout():



    
    return dbc.Container(
        [
            dbc.Row([
                dbc.Col(html.H1("Main Layout", className="text-center text-primary mb-4"), width=12),
                dbc.Col(dcc.Graph(
                    id="graph",
                    figure=generate_choropleth(),
                    className="dbc"
                ),
                width=12,
                className="mb-4"
                ),
                dbc.Col(
                    dcc.RangeSlider(
                        0, 20, 1,
                        value=[2, 4],
                    ),
                    className="dbc",
                    width=12
                ),
                dbc.Col(
                    dcc.Checklist(
                        options=[
                            {'label': 'Option 1', 'value': 'opt1'},
                            {'label': 'Option 2', 'value': 'opt2'},
                            {'label': 'Option 3', 'value': 'opt3'},
                        ],
                        value=['opt1', 'opt3'],
                        inline=True,
                        className="dbc d-flex flex-row gap-3",
                        id = "checklist-col"
                    ),
                    width=4
                ),
                dbc.Col(
                    dbc.Button("Primary", color="primary", className="pe-3 ps-3", id="primary-button", n_clicks=0),
                    className="d-flex justify-content-center",
                    width=4 
                ),
                dbc.Col(
                    dcc.RadioItems(['New York City', 'Montreal','San Francisco'], 'Montreal', inline=True,
                                   className="dbc d-flex flex-row gap-3"),
                    width=4,
                    id = "radio-items-col",
                )
            ]),

        ]
    ),

    


