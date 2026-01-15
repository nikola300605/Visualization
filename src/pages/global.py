import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, callback, Input, Output
from src.data_loading.load_data import load_data_into_df

dash.register_page(__name__, path="/global", name="Global", order=1)

DF = load_data_into_df()

def _numeric_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c != "Country" and pd.api.types.is_numeric_dtype(df[c])]


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

LOWER_IS_BETTER = {
    "Population_Below_Poverty_Line_percent",
    "Infant_Mortality_Rate",
    "Unemployment_Rate_percent",
    "Youth_Unemployment_Rate_percent",
    "Adolescent_Birth_Rate_(births_per_1,000_women_ages_15-19)",
    "Death_Rate",
}

if not ECON_COLS:
    ECON_COLS = _numeric_cols(DF)
if not SOCIAL_COLS:
    SOCIAL_COLS = _numeric_cols(DF)

DEFAULT_X = "Real_GDP_per_Capita_USD"
DEFAULT_Y = "Life_Expectancy_at_Birth_(years)"


def build_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    use_log_x: bool,
    show_reg_line: bool,
    top_n: int,
) -> go.Figure:
    d = df[["Country", x_col, y_col]].copy()
    d = d.dropna(subset=[x_col, y_col])

    # Avoid log(0) / log(negative)
    if use_log_x:
        d = d[d[x_col] > 0].copy()
        x_for_model = np.log(d[x_col].astype(float).values)
        x_label = f"log({x_col})"
    else:
        x_for_model = d[x_col].astype(float).values
        x_label = x_col

    y = d[y_col].astype(float).values

    # Simple linear fit: y_hat = a + b*x
    b, a = np.polyfit(x_for_model, y, 1)
    y_hat = a + b * x_for_model
    resid = y - y_hat
    if y_col in LOWER_IS_BETTER:
        resid = -resid
    d["predicted"] = y_hat
    d["residual"] = resid

    # Rank extremes
    d_sorted = d.sort_values("residual")
    under = d_sorted.head(top_n)
    over = d_sorted.tail(top_n)

    # Base scatterplot (all points)
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=d[x_col] if not use_log_x else d[x_col],
            y=d[y_col],
            mode="markers",
            name="Countries",
            marker=dict(size=7, opacity=0.45),
            customdata=np.stack([d["Country"], d["predicted"], d["residual"]], axis=1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                f"{x_col}: %{{x}}<br>"
                f"{y_col}: %{{y}}<br>"
                "Expected: %{customdata[1]:.2f}<br>"
                "Residual: %{customdata[2]:+.2f}<extra></extra>"
            ),
        )
    )

    # Regression line
    if show_reg_line:
        # Build line across the observed x-range
        x_min, x_max = d[x_col].min(), d[x_col].max()
        x_line = np.linspace(x_min, x_max, 200)

        if use_log_x:
            x_model_line = np.log(x_line)
        else:
            x_model_line = x_line

        y_line = a + b * x_model_line

        fig.add_trace(
            go.Scatter(
                x=x_line,
                y=y_line,
                mode="lines",
                name="Expected (regression)",
                line=dict(dash="dash"),
            )
        )

    # Highlight over/under as separate traces
    fig.add_trace(
        go.Scatter(
            x=under[x_col],
            y=under[y_col],
            mode="markers+text",
            name="Under-performing",
            marker=dict(size=10),
            text=under["Country"],
            textposition="top center",
            textfont=dict(size=10),
            customdata=np.stack([under["Country"], under["predicted"], under["residual"]], axis=1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                f"{x_col}: %{{x}}<br>"
                f"{y_col}: %{{y}}<br>"
                "Expected: %{customdata[1]:.2f}<br>"
                "Residual: %{customdata[2]:+.2f}<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=over[x_col],
            y=over[y_col],
            mode="markers+text",
            name="Over-performing",
            marker=dict(size=10),
            text=over["Country"],
            textposition="top center",
            textfont=dict(size=10),
            customdata=np.stack([over["Country"], over["predicted"], over["residual"]], axis=1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                f"{x_col}: %{{x}}<br>"
                f"{y_col}: %{{y}}<br>"
                "Expected: %{customdata[1]:.2f}<br>"
                "Residual: %{customdata[2]:+.2f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=f"{y_col} vs {x_col} (highlighting over/under-performance)",
        xaxis_title=x_col if not use_log_x else f"{x_col} (log used in model)",
        yaxis_title=y_col,
        legend_title="",
        margin=dict(l=10, r=10, t=55, b=10),
        height=650,
    )

    return fig

layout = dbc.Container(
    [
        html.H2("Global analysis", className="mb-3"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Economic indicator (X)"),
                        dcc.Dropdown(
                            id="global-x-col",
                            options=[{"label": c, "value": c} for c in ECON_COLS],
                            value=DEFAULT_X,
                            clearable=False,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("Social indicator (Y)"),
                        dcc.Dropdown(
                            id="global-y-col",
                            options=[{"label": c, "value": c} for c in SOCIAL_COLS],
                            value=DEFAULT_Y,
                            clearable=False,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Label("Options"),
                        dbc.Checklist(
                            id="global-options",
                            options=[
                                {"label": "Use log(X) in regression", "value": "logx"},
                                {"label": "Show regression line", "value": "reg"},
                            ],
                            value=["logx", "reg"],
                        ),
                        dbc.Label("Highlight top N over/under", className="mt-2"),
                        dcc.Slider(
                            id="global-top-n",
                            min=3,
                            max=15,
                            step=1,
                            value=8,
                            marks={3: "3", 8: "8", 15: "15"},
                        ),
                    ],
                    md=4,
                ),
            ],
            className="mb-3",
        ),
        dcc.Graph(id="global-scatter", config={"displayModeBar": True}),
    ],
    fluid=True,
)

@callback(
    Output("global-scatter", "figure"),
    Input("global-x-col", "value"),
    Input("global-y-col", "value"),
    Input("global-options", "value"),
    Input("global-top-n", "value"),
)
def update_global_scatter(x_col: str, y_col: str, options: list[str], top_n: int):
    use_log_x = "logx" in (options or [])
    show_reg = "reg" in (options or [])
    return build_scatter(DF, x_col, y_col, use_log_x, show_reg, int(top_n))


