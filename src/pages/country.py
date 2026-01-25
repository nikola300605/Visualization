import urllib.parse
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output

from src.data_loading.load_data import load_data_into_df

dash.register_page(__name__, path="/country", name="Country", order=10)

# region CONSTANTS

# Metric labels for human readble 
METRIC_LABELS = {
    "Real_GDP_per_Capita_USD": "GDP per Capita (USD)",
    "Real_GDP_PPP_billion_USD": "Real GDP PPP (Billion USD)",
    "GDP_Official_Exchange_Rate_billion_USD": "GDP at Official Rate (Billion USD)",
    "Real_GDP_Growth_Rate_percent": "Real GDP Growth Rate (%)",
    "Public_Debt_percent_of_GDP": "Public Debt (% of GDP)",
    "Budget_billion_USD": "Budget (Billion USD)",
    "Budget_Deficit_percent_of_GDP": "Budget Deficit (% of GDP)",
    "Exports_billion_USD": "Exports (Billion USD)",
    "Imports_billion_USD": "Imports (Billion USD)",
    "Exchange_Rate_per_USD": "Exchange Rate (per USD)",
    "Unemployment_Rate_percent": "Unemployment Rate (%)",
    "Youth_Unemployment_Rate_percent": "Youth Unemployment (%)",
    "Life_Expectancy_at_Birth_(years)": "Life Expectancy (years)",
    "Infant_Mortality_Rate": "Infant Mortality (per 1,000)",
    "Human_Development_Index_(value)": "HDI",
    "Inequality-adjusted_Human_Development_Index_(value)": "Inequality-adjusted HDI",
    "Expected_Years_of_Schooling_(years)": "Expected Years of Schooling",
    "Total_Literacy_Rate [%]": "Literacy Rate (%)",
    "Male_Literacy_Rate [%]": "Male Literacy Rate (%)",
    "Female_Literacy_Rate [%]": "Female Literacy Rate (%)",
    "Population_Below_Poverty_Line_percent": "Poverty Rate (%)",
    "Adolescent_Birth_Rate_(births_per_1,000_women_ages_15-19)": "Adolescent Birth Rate (per 1,000)",
    "Total_Fertility_Rate": "Fertility Rate (births/woman)",
    "Median_Age": "Median Age (years)",
    "Death_Rate": "Death Rate (per 1,000)",
    "Population_Growth_Rate_(percentage)": "Population Growth Rate (%)",
    "electricity_access_percent": "Electricity Access (%)",
    "internet_penetration_rate": "Internet Penetration (%)",
    "broadband_fixed_subscriptions_rate": "Broadband Subscriptions (%)",
    "road_density_log": "Road Density (log10)",
}

ECON_COLS = [
    "Real_GDP_per_Capita_USD",
    "Real_GDP_PPP_billion_USD",
    "GDP_Official_Exchange_Rate_billion_USD",
    "Real_GDP_Growth_Rate_percent",
    "Public_Debt_percent_of_GDP",
    "Budget_billion_USD",
    "Budget_Deficit_percent_of_GDP",
    "Exports_billion_USD",
    "Imports_billion_USD",
    "Exchange_Rate_per_USD",
    "Unemployment_Rate_percent",
    "Youth_Unemployment_Rate_percent",
]

SOCIAL_COLS = [
    "Life_Expectancy_at_Birth_(years)",
    "Infant_Mortality_Rate",
    "Human_Development_Index_(value)",
    "Inequality-adjusted_Human_Development_Index_(value)",
    "Expected_Years_of_Schooling_(years)",
    "Total_Literacy_Rate [%]",
    "Male_Literacy_Rate [%]",
    "Female_Literacy_Rate [%]",
    "Population_Below_Poverty_Line_percent",
    "Adolescent_Birth_Rate_(births_per_1,000_women_ages_15-19)",
    "Total_Fertility_Rate",
    "Median_Age",
    "Death_Rate",
]

LEADERBOARD_METRICS = [
    "Real_GDP_per_Capita_USD",
    "Human_Development_Index_(value)",
    "road_density_log",
    "internet_penetration_rate",
    "Life_Expectancy_at_Birth_(years)",
    "Total_Literacy_Rate [%]",
    "broadband_fixed_subscriptions_rate",
]

INFRA_COLS = [
    "electricity_access_percent",
    "internet_penetration_rate",
    "broadband_fixed_subscriptions_rate",
    "road_density_log",
]

DEFAULT_SNAPSHOT_METRICS = [
    "Real_GDP_per_Capita_USD",
    "Human_Development_Index_(value)",
    "Life_Expectancy_at_Birth_(years)",
    "Infant_Mortality_Rate",
    "Total_Fertility_Rate",
    "internet_penetration_rate",
]

DEFAULT_CTX_X = "Real_GDP_per_Capita_USD"
DEFAULT_CTX_Y = "Life_Expectancy_at_Birth_(years)"

LOWER_IS_BETTER = {
    "Population_Below_Poverty_Line_percent",
    "Infant_Mortality_Rate",
    "Unemployment_Rate_percent",
    "Youth_Unemployment_Rate_percent",
    "Adolescent_Birth_Rate_(births_per_1,000_women_ages_15-19)",
    "Death_Rate",
}

RADAR_METRICS = [
    "Real_GDP_per_Capita_USD",
    "Human_Development_Index_(value)",
    "Life_Expectancy_at_Birth_(years)",
    "Infant_Mortality_Rate",
    "Total_Fertility_Rate",
    "internet_penetration_rate",
    "road_density_log",
    "Total_Literacy_Rate [%]",
]

DEMO_PRESSURE_COLS = [
    "Median_Age",
    "Total_Fertility_Rate",
    "Population_Growth_Rate_(percentage)",
    "Youth_Unemployment_Rate_percent",
    "Adolescent_Birth_Rate_(births_per_1,000_women_ages_15-19)",
]

INFRA_COMPARISON_COLS = [
    "electricity_access_percent",
    "internet_penetration_rate",
    "broadband_fixed_subscriptions_rate",
    "road_density_log",
]

# sets for comparison
METRIC_SETS = {
    "Snapshot": DEFAULT_SNAPSHOT_METRICS,
    "Economy": ECON_COLS,
    "Social": SOCIAL_COLS,
    "Infrastructure": INFRA_COLS,
}

# endregion

# region HELPER FUNCTIONS

def metric_label(col):
    """Convert column name to human-friendly label."""
    if col in METRIC_LABELS:
        return METRIC_LABELS[col]
    # fallback to replace underscores and shii
    label = col.replace("_", " ").replace("  ", " ").strip()
    return label


def safe_get(row_df, col):
    """Return scalar value from row, or None if missing/NaN."""
    if col not in row_df.columns:
        return None
    val = row_df[col].iloc[0] if not row_df.empty else None
    if pd.isna(val):
        return None
    return val


def fmt_value(col, val):
    """Format value based on column name."""
    if val is None or pd.isna(val):
        return "No data"
    
    if "percent" in col.lower() or "%" in col:
        return f"{val:.1f}%"
    elif "usd" in col.lower():
        return f"${val:,.0f}"
    elif "(years)" in col.lower() or "age" in col.lower():
        return f"{val:.1f}"
    else:
        if isinstance(val, (int, np.integer)):
            return f"{val:,}"
        return f"{val:.2f}"


def world_stat(df, col, how="median"):
    """Return median or mean of column, ignoring NaN."""
    valid = df[col].dropna()
    if valid.empty:
        return None
    if how == "median":
        return valid.median()
    else:
        return valid.mean()


def percentile_of_country(df, col, iso3):
    """Return 0-100 percentile rank where higher is always better.
    
    For LOWER_IS_BETTER metrics (e.g., Infant Mortality), the percentile
    is inverted so that lower values receive higher percentiles.
    Uses rank-based approach with average method for ties.
    """
    if col not in df.columns:
        return None
    s = df.set_index("ISO3")[col]
    if iso3 not in s.index:
        return None
    if pd.isna(s.loc[iso3]):
        return None
    
    # rank using percentage method (0-1 scale), i forgor the science name of this 
    ranks = s.rank(method="average", pct=True) * 100
    pct = float(ranks.loc[iso3])
    
    #invert for metrics where lower is better
    if col in LOWER_IS_BETTER:
        pct = 100.0 - pct
    
    return pct

# endregion

# region LAYOUT

layout = dbc.Container(
    [
        dcc.Store(id="country-df-store", data=None, storage_type="memory"),
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

# endregion

# region MAIN CALLBACKS

@callback(
    Output("country-df-store", "data"),
    Input("url", "search"),
)
def load_df_once(search):
    """Load dataframe once per page visit and store in dcc.Store."""
    df = load_data_into_df()
    return df.to_json(date_format="iso", orient="split")


def _get_df_from_store(store_data):
    """Helper to deserialize dataframe from store; fallback to loading if None."""
    if store_data is None:
        return load_data_into_df()
    return pd.read_json(store_data, orient="split")


@callback(
    Output("country-page-content", "children"),
    Input("url", "pathname"),
    Input("url", "search"),
    Input("country-df-store", "data"),
)
def render_country_page(pathname, search, store_data):
    """Render the main country page layout."""
    if pathname != "/country":
        return ""

    if not search:
        return dbc.Alert("No country selected. Return to the map.", color="warning")

    qs = urllib.parse.parse_qs(search.lstrip("?"))
    iso3 = qs.get("iso3", [None])[0]

    if not iso3:
        return dbc.Alert("No country selected. Return to the map.", color="warning")

    df = _get_df_from_store(store_data)
    row = df[df["ISO3"] == iso3]

    if row.empty:
        return dbc.Alert(f"Unknown ISO3 code: {iso3}", color="danger")

    country = safe_get(row, "Country") or iso3
    capital = safe_get(row, "Capital")
    govt_type = safe_get(row, "Government_Type")

    #Header
    header_text = f"ISO3: {iso3}"
    if capital:
        header_text += f" | Capital: {capital}"
    if govt_type:
        header_text += f" | {govt_type}"

    header = dbc.Card(
        dbc.CardBody(
            [
                html.H2(country, className="mb-2"),
                html.Small(header_text, className="text-muted"),
            ]
        ),
        className="mb-4",
    )

    #Snapshot KPIs
    snapshot = dcc.Loading(
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Key Metrics", className="mb-3"),
                    html.Div(id="snapshot-kpis"),
                ]
            ),
            className="mb-4",
        ),
        type="default",
    )

    #Tabs - dont touch
    tabs = dbc.Tabs(
        [
            dbc.Tab(
                label="Context",
                children=[
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id="ctx-x-dropdown",
                                                options=[
                                                    {"label": metric_label(c), "value": c}
                                                    for c in ECON_COLS
                                                ],
                                                value=DEFAULT_CTX_X,
                                            ),
                                            md=4,
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id="ctx-y-dropdown",
                                                options=[
                                                    {"label": metric_label(c), "value": c}
                                                    for c in SOCIAL_COLS
                                                ],
                                                value=DEFAULT_CTX_Y,
                                            ),
                                            md=4,
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            dcc.Checklist(
                                                id="ctx-checklist",
                                                options=[
                                                    {"label": " Log X-axis", "value": "logx"},
                                                    {"label": " Regression line", "value": "regline"},
                                                ],
                                                value=["regline"],
                                                inline=True,
                                            ),
                                            md=4,
                                            className="mb-3",
                                        ),
                                    ]
                                )
                            ]
                        ),
                        className="mb-4",
                    ),
                    dcc.Loading(
                        dcc.Graph(id="ctx-scatter"),
                        type="default",
                    ),
                    dcc.Loading(
                        dcc.Graph(id="ctx-percentiles"),
                        type="default",
                    ),
                ],
                className="p-3",
            ),
            dbc.Tab(
                label="Deep Dives",
                children=[
                    dcc.Loading(
                        dcc.Graph(id="deep-radar"),
                        type="default",
                    ),
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                dcc.Loading(
                                    dcc.Graph(id="demo-bars"),
                                    type="default",
                                ),
                                title="Demographic & Labor Pressures",
                            ),
                            dbc.AccordionItem(
                                dcc.Loading(
                                    dcc.Graph(id="infra-bars"),
                                    type="default",
                                ),
                                title="Infrastructure & Access",
                            ),
                        ],
                        className="mt-3",
                    ),
                ],
                className="p-3",
            ),
            dbc.Tab(
                label="Compare",
                children=[
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Label("Comparison Method"),
                                                dcc.Dropdown(
                                                    id="compare-method",
                                                    options=[
                                                        {"label": "Similar GDP per capita", "value": "gdp"},
                                                        {"label": "Similar HDI", "value": "hdi"},
                                                        {"label": "Manual Selection", "value": "manual"},
                                                    ],
                                                    value="gdp",
                                                ),
                                            ],
                                            md=3,
                                        ),
                                        dbc.Col(
                                            [
                                                html.Label("Select Countries", id="manual-label"),
                                                dcc.Dropdown(
                                                    id="compare-manual",
                                                    multi=True,
                                                    style={"display": "none"},
                                                ),
                                            ],
                                            md=3,
                                        ),
                                        dbc.Col(
                                            [
                                                html.Label("Metric Category"),
                                                dcc.Dropdown(
                                                    id="compare-metric-set",
                                                    options=[
                                                        {"label": k, "value": k}
                                                        for k in METRIC_SETS.keys()
                                                    ],
                                                    value="Snapshot",
                                                    clearable=False,
                                                ),
                                            ],
                                            md=3,
                                        ),
                                        dbc.Col(
                                            [
                                                html.Label("Metric"),
                                                dcc.Dropdown(
                                                    id="compare-metric",
                                                    options=[
                                                        {"label": metric_label(c), "value": c}
                                                        for c in METRIC_SETS["Snapshot"]
                                                    ],
                                                    value=METRIC_SETS["Snapshot"][0],
                                                    clearable=False,
                                                ),
                                            ],
                                            md=3,
                                        ),
                                    ]
                                )
                            ]
                        ),
                        className="mb-4",
                    ),
                    dcc.Loading(
                        dcc.Graph(id="compare-chart"),
                        type="default",
                    ),
                ],
                className="p-3",
            ),
        ],
        className="mt-4",
    )

    return dbc.Container(
        [header, snapshot, tabs],
        fluid=True,
    )

# endregion

# region CALLBACKS

@callback(
    Output("snapshot-kpis", "children"),
    Input("url", "search"),
    Input("country-df-store", "data"),
)
def update_snapshot_kpis(search, store_data):
    """Update KPI snapshot cards."""
    if not search:
        return dbc.Alert("No data", color="light")

    qs = urllib.parse.parse_qs(search.lstrip("?"))
    iso3 = qs.get("iso3", [None])[0]

    if not iso3:
        return dbc.Alert("No data", color="light")

    df = _get_df_from_store(store_data)
    row = df[df["ISO3"] == iso3]

    if row.empty:
        return dbc.Alert("No data", color="light")

    cards = []
    for metric in DEFAULT_SNAPSHOT_METRICS:
        val = safe_get(row, metric)
        fmt_val = fmt_value(metric, val)
        world_median = world_stat(df, metric, how="median")
        percentile = percentile_of_country(df, metric, iso3)

        context_str = "No context"
        if world_median is not None and percentile is not None:
            context_str = f"World: {fmt_value(metric, world_median)} | Percentile: {percentile:.0f}"

        card = dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Small(metric_label(metric), className="text-muted"),
                        html.H5(fmt_val, className="mt-2 mb-3"),
                        html.Small(context_str, className="text-muted d-block"),
                    ]
                ),
            ),
            md=4,
            className="mb-3",
        )
        cards.append(card)

    return dbc.Row(cards)

@callback(
    Output("ctx-scatter", "figure"),
    Input("url", "search"),
    Input("ctx-x-dropdown", "value"),
    Input("ctx-y-dropdown", "value"),
    Input("ctx-checklist", "value"),
    Input("country-df-store", "data"),
)
def update_context_scatter(search, x_col, y_col, checklist, store_data):
    """Update context scatter plot."""
    if not search or not x_col or not y_col:
        return go.Figure().add_annotation(text="No data")

    qs = urllib.parse.parse_qs(search.lstrip("?"))
    iso3 = qs.get("iso3", [None])[0]

    if not iso3:
        return go.Figure().add_annotation(text="No data")

    df = _get_df_from_store(store_data)

    #Prepare data
    plot_df = df[[x_col, y_col, "Country", "ISO3"]].dropna()

    if plot_df.empty:
        return go.Figure().add_annotation(text="No data for selected metrics")

    use_log_x = "logx" in checklist
    show_regline = "regline" in checklist

    #Prepare X data
    x_data = plot_df[x_col].values
    if use_log_x:
        x_plot = np.log10(np.maximum(x_data, 1e-10))
        x_label = metric_label(x_col) + " (log10)"
    else:
        x_plot = x_data
        x_label = metric_label(x_col)

    y_plot = plot_df[y_col].values
    y_label = metric_label(y_col)

    fig = go.Figure()

    #Add all countries
    fig.add_trace(
        go.Scatter(
            x=x_plot,
            y=y_plot,
            mode="markers",
            marker=dict(size=8, opacity=0.6, color="steelblue"),
            text=plot_df["Country"],
            hovertemplate="<b>%{text}</b><br>" + metric_label(x_col) + ": %{customdata[0]:,.0f}<br>" + metric_label(y_col) + ": %{y:,.1f}<extra></extra>",
            customdata=np.column_stack([x_data]),
            name="Countries",
        )
    )

    #hghlight selected country - not sure if it works
    selected_row = plot_df[plot_df["ISO3"] == iso3]
    if not selected_row.empty:
        sel_x = selected_row[x_col].iloc[0]
        sel_y = selected_row[y_col].iloc[0]
        if use_log_x:
            sel_x_plot = np.log10(max(sel_x, 1e-10))
        else:
            sel_x_plot = sel_x

        fig.add_trace(
            go.Scatter(
                x=[sel_x_plot],
                y=[sel_y],
                mode="markers",
                marker=dict(
                    size=14,
                    color="red",
                    line=dict(width=2, color="darkred"),
                ),
                text=[selected_row["Country"].iloc[0]],
                hovertemplate="<b>%{text}</b> (Selected)<extra></extra>",
                name="Selected",
            )
        )

        #add regression line if requested - remove prob, needs error handling
        if show_regline and len(plot_df) > 2:
            try:
                z = np.polyfit(x_plot, y_plot, 1)
                p = np.poly1d(z)
                x_line = np.linspace(x_plot.min(), x_plot.max(), 100)
                y_line = p(x_line)
                fig.add_trace(
                    go.Scatter(
                        x=x_line,
                        y=y_line,
                        mode="lines",
                        line=dict(color="gray", dash="dash"),
                        name="Trend",
                    )
                )

                # Residual annot
                residual = sel_y - p(sel_x_plot)
                fig.add_annotation(
                    x=sel_x_plot,
                    y=sel_y,
                    text=f"Residual: {residual:.2f}",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=1,
                    arrowcolor="red",
                    ax=30,
                    ay=-30,
                )
            except Exception:
                pass

    fig.update_layout(
        title=f"{y_label} vs {x_label}",
        xaxis_title=x_label,
        yaxis_title=y_label,
        hovermode="closest",
        height=500,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


@callback(
    Output("ctx-percentiles", "figure"),
    Input("url", "search"),
    Input("country-df-store", "data"),
)
def update_context_percentiles(search, store_data):
    """Update percentile snapshot."""
    if not search:
        return go.Figure().add_annotation(text="No data")

    qs = urllib.parse.parse_qs(search.lstrip("?"))
    iso3 = qs.get("iso3", [None])[0]

    if not iso3:
        return go.Figure().add_annotation(text="No data")

    df = _get_df_from_store(store_data)
    row = df[df["ISO3"] == iso3]

    if row.empty:
        return go.Figure().add_annotation(text="No data")

    percentiles = []
    metrics_labels = []

    for metric in DEFAULT_SNAPSHOT_METRICS:
        pct = percentile_of_country(df, metric, iso3)
        if pct is not None:
            percentiles.append(pct)
            metrics_labels.append(metric_label(metric))

    if not percentiles:
        return go.Figure().add_annotation(text="No data for percentiles")

    fig = go.Figure(
        data=[
            go.Bar(
                x=percentiles,
                y=metrics_labels,
                orientation="h",
                marker=dict(color="steelblue"),
            )
        ]
    )

    fig.update_layout(
        title="Percentile Ranking (higher is better)",
        xaxis_title="Percentile (0-100)",
        height=400,
        xaxis=dict(range=[0, 100]),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


@callback(
    Output("deep-radar", "figure"),
    Input("url", "search"),
    Input("country-df-store", "data"),
)
def update_radar(search, store_data):
    """Update radar profile."""
    if not search:
        return go.Figure().add_annotation(text="No data")

    qs = urllib.parse.parse_qs(search.lstrip("?"))
    iso3 = qs.get("iso3", [None])[0]

    if not iso3:
        return go.Figure().add_annotation(text="No data")

    df = _get_df_from_store(store_data)
    row = df[df["ISO3"] == iso3]

    if row.empty:
        return go.Figure().add_annotation(text="No data")

    #Build radar data for available metrics -look it up
    radar_values = []
    radar_labels = []

    for metric in RADAR_METRICS:
        if metric not in df.columns:
            continue

        val = safe_get(row, metric)
        if val is None:
            continue

        # Min-max normalize across all
        valid = df[metric].dropna()
        if valid.empty:
            continue

        min_val = valid.min()
        max_val = valid.max()

        if max_val == min_val:
            normalized = 0.5
        else:
            normalized = (val - min_val) / (max_val - min_val)

        # Invert "bad when high"
        if metric in LOWER_IS_BETTER:
            normalized = 1 - normalized

        radar_values.append(normalized)
        radar_labels.append(metric_label(metric))

    if not radar_values:
        return go.Figure().add_annotation(text="No data for radar")

    # World median reference - align with radar_labels hopefuly
    world_values = []
    radar_metrics_used = [m for m in RADAR_METRICS if m in df.columns and safe_get(row, m) is not None]
    
    for metric in radar_metrics_used:
        world_med = world_stat(df, metric, how="median")
        if world_med is None:
            world_values.append(0.5)
        else:
            valid = df[metric].dropna()
            min_val = valid.min()
            max_val = valid.max()
            if max_val == min_val:
                normalized = 0.5
            else:
                normalized = (world_med - min_val) / (max_val - min_val)
            if metric in LOWER_IS_BETTER:
                normalized = 1 - normalized
            world_values.append(normalized)

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=radar_values + [radar_values[0]],
            theta=radar_labels + [radar_labels[0]],
            fill="toself",
            name=safe_get(row, "Country") or iso3,
            line=dict(color="steelblue"),
        )
    )

    fig.add_trace(
        go.Scatterpolar(
            r=world_values + [world_values[0]],
            theta=radar_labels + [radar_labels[0]],
            fill="toself",
            name="World Median",
            line=dict(color="gray", dash="dash"),
            opacity=0.5,
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Country Profile (normalized 0-1; higher is better)",
        height=500,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


@callback(
    Output("demo-bars", "figure"),
    Input("url", "search"),
    Input("country-df-store", "data"),
)
def update_demo_bars(search, store_data):
    """Update demographic pressure bars (normalized 0-1, higher is better)."""
    if not search:
        return go.Figure().add_annotation(text="No data")

    qs = urllib.parse.parse_qs(search.lstrip("?"))
    iso3 = qs.get("iso3", [None])[0]

    if not iso3:
        return go.Figure().add_annotation(text="No data")

    df = _get_df_from_store(store_data)
    row = df[df["ISO3"] == iso3]

    if row.empty:
        return go.Figure().add_annotation(text="No data")

    metrics_to_plot = []
    country_norm = []
    world_norm = []
    country_raw = []
    world_raw = []

    for metric in DEMO_PRESSURE_COLS:
        if metric not in df.columns:
            continue
        val = safe_get(row, metric)
        world_med = world_stat(df, metric, how="median")
        if val is None or world_med is None:
            continue

        valid = df[metric].dropna()
        if valid.empty:
            continue
        
        min_val = valid.min()
        max_val = valid.max()
        
        if max_val == min_val:
            country_normalized = 0.5
            world_normalized = 0.5
        else:
            country_normalized = (val - min_val) / (max_val - min_val)
            world_normalized = (world_med - min_val) / (max_val - min_val)
        
        if metric in LOWER_IS_BETTER:
            country_normalized = 1.0 - country_normalized
            world_normalized = 1.0 - world_normalized
        
        metrics_to_plot.append(metric_label(metric))
        country_norm.append(country_normalized)
        world_norm.append(world_normalized)
        country_raw.append(val)
        world_raw.append(world_med)

    if not metrics_to_plot:
        return go.Figure().add_annotation(text="No data for demographics")

    # Prepare customdata with raw values (2D array for each bar)
    country_customdata = np.column_stack([country_raw])
    world_customdata = np.column_stack([world_raw])

    fig = go.Figure(
        data=[
            go.Bar(
                name="Country",
                x=metrics_to_plot,
                y=country_norm,
                marker_color="steelblue",
                hovertemplate="<b>Country</b><br>%{x}<br>Normalized: %{y:.2f}<br>Raw: %{customdata[0]:.2f}<extra></extra>",
                customdata=country_customdata,
            ),
            go.Bar(
                name="World Median",
                x=metrics_to_plot,
                y=world_norm,
                marker_color="lightslategray",
                hovertemplate="<b>World Median</b><br>%{x}<br>Normalized: %{y:.2f}<br>Raw: %{customdata[0]:.2f}<extra></extra>",
                customdata=world_customdata,
            ),
        ]
    )

    fig.update_layout(
        title="Demographic & Labor Pressures (normalized 0-1; higher is better)",
        barmode="group",
        height=400,
        xaxis_tickangle=-45,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


@callback(
    Output("infra-bars", "figure"),
    Input("url", "search"),
    Input("country-df-store", "data"),
)
def update_infra_bars(search, store_data):
    """Update infrastructure bars (normalized 0-1, higher is better)."""
    if not search:
        return go.Figure().add_annotation(text="No data")

    qs = urllib.parse.parse_qs(search.lstrip("?"))
    iso3 = qs.get("iso3", [None])[0]

    if not iso3:
        return go.Figure().add_annotation(text="No data")

    df = _get_df_from_store(store_data)
    row = df[df["ISO3"] == iso3]

    if row.empty:
        return go.Figure().add_annotation(text="No data")

    metrics_to_plot = []
    country_norm = []
    world_norm = []
    country_raw = []
    world_raw = []

    for metric in INFRA_COMPARISON_COLS:
        if metric not in df.columns:
            continue
        val = safe_get(row, metric)
        world_med = world_stat(df, metric, how="median")
        if val is None or world_med is None:
            continue

        valid = df[metric].dropna()
        if valid.empty:
            continue
        
        min_val = valid.min()
        max_val = valid.max()
        
        if max_val == min_val:
            country_normalized = 0.5
            world_normalized = 0.5
        else:
            country_normalized = (val - min_val) / (max_val - min_val)
            world_normalized = (world_med - min_val) / (max_val - min_val)
        
        # Invert for "lower is better" (infrastructure typically higher is better, ithink
        if metric in LOWER_IS_BETTER:
            country_normalized = 1.0 - country_normalized
            world_normalized = 1.0 - world_normalized
        
        metrics_to_plot.append(metric_label(metric))
        country_norm.append(country_normalized)
        world_norm.append(world_normalized)
        country_raw.append(val)
        world_raw.append(world_med)

    if not metrics_to_plot:
        return go.Figure().add_annotation(text="No data for infrastructure")

    # Prepare customdata with raw values (2D array for each bar)
    country_customdata = np.column_stack([country_raw])
    world_customdata = np.column_stack([world_raw])

    fig = go.Figure(
        data=[
            go.Bar(
                name="Country",
                x=metrics_to_plot,
                y=country_norm,
                marker_color="mediumseagreen",
                hovertemplate="<b>Country</b><br>%{x}<br>Normalized: %{y:.2f}<br>Raw: %{customdata[0]:.2f}<extra></extra>",
                customdata=country_customdata,
            ),
            go.Bar(
                name="World Median",
                x=metrics_to_plot,
                y=world_norm,
                marker_color="darkseagreen",
                hovertemplate="<b>World Median</b><br>%{x}<br>Normalized: %{y:.2f}<br>Raw: %{customdata[0]:.2f}<extra></extra>",
                customdata=world_customdata,
            ),
        ]
    )

    fig.update_layout(
        title="Infrastructure & Access (normalized 0-1; higher is better)",
        barmode="group",
        height=400,
        xaxis_tickangle=-45,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


@callback(
    Output("compare-manual", "style"),
    Input("compare-method", "value"),
)
def toggle_manual_compare_visibility(method):
    """Show/hide manual country selector."""
    if method == "manual":
        return {"display": "block"}
    return {"display": "none"}


@callback(
    Output("compare-manual", "options"),
    Input("url", "search"),
    Input("country-df-store", "data"),
)
def update_manual_selector(search, store_data):
    """Update manual selector with all countries."""
    df = _get_df_from_store(store_data)
    # Filter out rows with NaN values in Country or ISO3
    valid_df = df[["Country", "ISO3"]].dropna()
    options = [
        {"label": row["Country"], "value": row["ISO3"]}
        for _, row in valid_df.iterrows()
    ]
    return options


@callback(
    Output("compare-metric", "options"),
    Output("compare-metric", "value"),
    Input("compare-metric-set", "value"),
)
def update_compare_metric_dropdown(metric_set):
    """Update metric dropdown based on selected set."""
    if metric_set not in METRIC_SETS:
        metric_set = "Snapshot"
    
    metrics = METRIC_SETS[metric_set]
    options = [{"label": metric_label(m), "value": m} for m in metrics]
    value = metrics[0]
    return options, value


@callback(
    Output("compare-chart", "figure"),
    Input("url", "search"),
    Input("compare-method", "value"),
    Input("compare-manual", "value"),
    Input("compare-metric", "value"),
    Input("country-df-store", "data"),
)
def update_compare_chart(search, method, manual_list, metric, store_data):
    """Update comparison chart with improved peer selection and formatting."""
    if not search or not metric:
        return go.Figure().add_annotation(text="No data")

    qs = urllib.parse.parse_qs(search.lstrip("?"))
    iso3 = qs.get("iso3", [None])[0]

    if not iso3:
        return go.Figure().add_annotation(text="No data")

    df = _get_df_from_store(store_data)
    country_row = df[df["ISO3"] == iso3]

    if country_row.empty or metric not in df.columns:
        return go.Figure().add_annotation(text="No data")

    # Determine peers
    if method == "gdp":
        col = "Real_GDP_per_Capita_USD"
        if col not in df.columns:
            return go.Figure().add_annotation(text="GDP column not found")
        country_val = safe_get(country_row, col)
        if country_val is None:
            peers = []
        else:
            # Exclude selected country from candidates
            valid = df[(df[col].notna()) & (df["ISO3"] != iso3)].copy()
            valid["diff"] = abs(valid[col] - country_val)
            peers = valid.nsmallest(5, "diff")["ISO3"].tolist()
    elif method == "hdi":
        col = "Human_Development_Index_(value)"
        if col not in df.columns:
            return go.Figure().add_annotation(text="HDI column not found")
        country_val = safe_get(country_row, col)
        if country_val is None:
            peers = []
        else:
            # Exclude selected country from candidates
            valid = df[(df[col].notna()) & (df["ISO3"] != iso3)].copy()
            valid["diff"] = abs(valid[col] - country_val)
            peers = valid.nsmallest(5, "diff")["ISO3"].tolist()
    else:  # manual
        peers = manual_list if manual_list else []

    #always include selected country first
    if iso3 not in peers:
        peers_ordered = [iso3] + peers
    else:
        peers_ordered = [iso3] + [p for p in peers if p != iso3]

    compare_df = df[df["ISO3"].isin(peers_ordered)].copy()

    if compare_df.empty or metric not in compare_df.columns:
        return go.Figure().add_annotation(text="No data for comparison")

    #rdop rows with missing metric
    compare_df = compare_df.dropna(subset=[metric])

    if compare_df.empty:
        return go.Figure().add_annotation(text="No data for selected metric")

    #reorder to match peers_ordered
    compare_df['iso_order'] = compare_df['ISO3'].map({iso: i for i, iso in enumerate(peers_ordered)})
    compare_df = compare_df.sort_values('iso_order').drop('iso_order', axis=1)

    #format values for hover
    formatted_vals = [fmt_value(metric, v) for v in compare_df[metric]]
    
    fig = go.Figure(
        data=[
            go.Bar(
                x=compare_df["Country"],
                y=compare_df[metric],
                marker_color=["red" if iso == iso3 else "steelblue" for iso in compare_df["ISO3"]],
                hovertemplate="<b>%{x}</b><br>" + metric_label(metric) + ": %{customdata}<extra></extra>",
                customdata=formatted_vals,
            )
        ]
    )

    fig.update_layout(
        title=f"{metric_label(metric)}",
        xaxis_title="Country",
        yaxis_title=metric_label(metric),
        height=400,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig

# endregion

