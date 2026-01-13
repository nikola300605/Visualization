import dash
import dash_bootstrap_components as dbc


dash.register_page(__name__, path="/global", name="Global", order=1)
layout = dbc.Container()