import pandas as pd
import numpy as np
import plotly.express as px
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import plotly.io as pio
from dash import Dash, html, dcc, Input, Output, State, clientside_callback, callback, Patch






def get_layout():
    fig = px.scatter(
                        x=np.random.randn(100),
                        y=np.random.randn(100),
                        title="Random Scatter Plot",
                        template="flatly")

    color_mode_switch =  html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="color-mode-switch"),
        dbc.Switch( id="color-mode-switch", value=False, className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="color-mode-switch"),
    ]
    )




    clientside_callback(
        """
        (switchOn) => {
        document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');  
        return window.dash_clientside.no_update
        }
        """,
        Output("color-mode-switch", "id"),
        Input("color-mode-switch", "value"),
    ) 


    @callback(
        Output(component_id="graph", component_property="figure"),
        Input(component_id="primary-button", component_property="n_clicks"),
        State(component_id="checklist-col", component_property="value")
    )

    def update_graph(n_clicks, checklist_values):
        new_fig = px.scatter(
            x=np.random.randn(100),
            y=np.random.randn(100),
            title=f"Button clicked {n_clicks} times; Checklist: {', '.join(checklist_values)}",
            template="flatly"
        )
        return new_fig
    
    return dbc.Container(
        [
            color_mode_switch,
            dbc.Row([
                dbc.Col(html.H1("Main Layout", className="text-center text-primary mb-4"), width=12),
                dbc.Col(dcc.Graph(
                    id="graph",
                    figure=fig
                ), width=12),
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

    


