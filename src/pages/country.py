import urllib.parse

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output

from src.data_loading.load_data import load_data_into_df

dash.register_page(__name__, path="/country", name="Country", order=10)

layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [
                    html.H2("Country Detail", className="mb-3"),
                    dcc.Loading(
                        html.Div(id="country-page-content"),
                        type="default",
                    ),
                ],
                width=12,
            )
        )
    ],
    fluid=True,
)

@callback(
    Output("country-page-content", "children"),
    Input("url", "pathname"),
    Input("url", "search"),
)
def render_country_page(pathname, search):
    print("COUNTRY CALLBACK:", pathname, search)

    if pathname != "/country":
        return ""

    if not search:
        return dbc.Alert("No country selected. Return to the map.", color="warning")

    qs = urllib.parse.parse_qs(search.lstrip("?"))
    iso3 = qs.get("iso3", [None])[0]

    if not iso3:
        return dbc.Alert("No country selected. Return to the map.", color="warning")

    df = load_data_into_df()
    row = df[df["ISO3"] == iso3]

    if row.empty:
        return dbc.Alert(f"Unknown ISO3 code: {iso3}", color="danger")

    country = row.iloc[0]["Country"]

    return dbc.Card(
        dbc.CardBody(
            [
                html.H3(country, className="mb-2"),
                html.Div(f"ISO3: {iso3}"),
            ]
        ),
        className="mt-2",
    )
