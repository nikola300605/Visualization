import urllib.parse
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
from src.data_loading.load_data import load_data_into_df

dash.register_page(__name__, path="/country", name="Country", order=10)

layout = dbc.Container(
    [
        dcc.Location(id="country-page-location", refresh=False),
        html.Div(id="country-page-content"),
    ],
    fluid=True,
)


@callback(Output("country-page-content", "children"), Input("country-page-location", "search"))
def render_country_page(search):
    if not search:
        return html.P("No country selected. Return to the map.")
    qs = urllib.parse.parse_qs(search.lstrip("?"))
    iso3 = qs.get("iso3", [None])[0]
    if not iso3:
        return html.P("No country selected. Return to the map.")
    # Lazy-load merged data (may be slow on first load)
    df = load_data_into_df()
    row = df[df["ISO3"] == iso3]
    country = row["Country"].iloc[0] if not row.empty else iso3
    # Placeholder content — replace with visualizations later
    return html.Div([html.H3(country), html.P(f"ISO3: {iso3}")])
