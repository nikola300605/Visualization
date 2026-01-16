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

LEADERBOARD_METRICS = [
    "Real_GDP_per_Capita_USD",
    "Human_Development_Index_(value)",
    "road_density_log",
    "internet_penetration_rate",
    "Life_Expectancy_at_Birth_(years)",
    "Total_Literacy_Rate [%]",
    "broadband_fixed_subscriptions_rate",
]

LOWER_IS_BETTER_LEADERBOARD = {
    "Infant_Mortality_Rate",
    "Unemployment_Rate_percent",
    "Population_Below_Poverty_Line_percent",
    "Death_Rate",
}

LOWER_IS_BETTER = {
    "Population_Below_Poverty_Line_percent",
    "Infant_Mortality_Rate",
    "Unemployment_Rate_percent",
    "Youth_Unemployment_Rate_percent",
    "Adolescent_Birth_Rate_(births_per_1,000_women_ages_15-19)",
    "Death_Rate",
}

CORR_COLS = [
    "Real_GDP_per_Capita_USD",
    "Life_Expectancy_at_Birth_(years)",
    "Total_Literacy_Rate [%]",
    "Expected_Years_of_Schooling_(years)",
    "Population_Below_Poverty_Line_percent",
    "Infant_Mortality_Rate",
    "Total_Fertility_Rate",
    "Median_Age",
]

if not ECON_COLS:
    ECON_COLS = _numeric_cols(DF)
if not SOCIAL_COLS:
    SOCIAL_COLS = _numeric_cols(DF)

DEFAULT_X = "Real_GDP_per_Capita_USD"
DEFAULT_Y = "Life_Expectancy_at_Birth_(years)"
DEFAULT_LEADERBOARD_METRIC = "Real_GDP_per_Capita_USD"

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

    if use_log_x:
        d = d[d[x_col] > 0].copy()
        x_for_model = np.log(d[x_col].astype(float).values)
        x_label = f"log({x_col})"
    else:
        x_for_model = d[x_col].astype(float).values
        x_label = x_col

    y = d[y_col].astype(float).values

    b, a = np.polyfit(x_for_model, y, 1)
    y_hat = a + b * x_for_model
    resid = y - y_hat
    if y_col in LOWER_IS_BETTER:
        resid = -resid
    d["predicted"] = y_hat
    d["residual"] = resid

    d_sorted = d.sort_values("residual")
    under = d_sorted.head(top_n)
    over = d_sorted.tail(top_n)

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

    if show_reg_line:
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
        title=dict(
        text="Social vs Economic indicator",
        font=dict(size=18),
        x=0.5,),
        xaxis_title=x_col if not use_log_x else f"{x_col} (log used in model)",
        yaxis_title=y_col,
        legend_title="",
        margin=dict(l=10, r=10, t=55, b=10),
    )

    return fig

def build_correlation_heatmap(df: pd.DataFrame, cols: list[str]) -> go.Figure:
    data = df[cols].dropna()
    corr = data.corr()

    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale="RdBu",
            zmid=0,
            colorbar=dict(title="Correlation"),
            hovertemplate=(
                "<b>%{x}</b> vs <b>%{y}</b><br>"
                "Correlation: %{z:.2f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text="Correlation between development indicators",
            font=dict(
                size=22,
                family="Arial",
                color="white",
            ),
        ),
        xaxis=dict(tickangle=45),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=80, r=20, t=60, b=80),
    )

    return fig

def build_global_ranking(df: pd.DataFrame, metric: str, top_n: int = 50, show_bottom: bool = False) -> go.Figure:
    data = df[["Country", metric]].copy().dropna()
    
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available for selected metric", showarrow=False)
        return fig
    
    values = data[metric].astype(float)
    if metric in LOWER_IS_BETTER_LEADERBOARD:
        values = -values
    
    data['Score'] = values
    
    min_val, max_val = data['Score'].min(), data['Score'].max()
    if max_val > min_val:
        data['Score'] = (data['Score'] - min_val) / (max_val - min_val) * 100
    
    if show_bottom:
        ranking = data.sort_values('Score', ascending=True).reset_index(drop=True)  # Lowest first
        title_suffix = f" BOTTOM {top_n}"
        color_scale = 'Reds'  # Red for "bad" performance
    else:
        ranking = data.sort_values('Score', ascending=False).reset_index(drop=True)  # Highest first
        title_suffix = f" TOP {top_n}"
        color_scale = 'Viridis'  # Green for "good" performance
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=ranking['Country'][:top_n],
        x=ranking['Score'][:top_n],
        orientation='h',
        marker=dict(
            color=ranking['Score'][:top_n], 
            colorscale=color_scale, 
            colorbar=dict(title="Score (0-100)")
        ), 
        text=ranking['Score'][:top_n].round(1),
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<br>Raw: %{customdata:.2f}<extra></extra>',
        customdata=ranking[metric][:top_n].round(2)
    ))
    
    fig.update_layout(
        title=f"🏆 {metric.replace('_', ' ').title()}{title_suffix} Countries",
        yaxis_categoryorder='array', 
        yaxis_categoryarray=ranking['Country'][:top_n].tolist(),
        height=600, 
        xaxis_title="Normalized Score (0-100)",
        margin=dict(l=250, r=20, t=60, b=20),
        font=dict(size=12)
    )
    
    return fig

layout = dbc.Container(
    [
        html.H1("Global analysis", className="mb-3"),

        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Performance vs expected outcome"),
                            dbc.CardBody(
                                [
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
                                                md=6,
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
                                                md=6,
                                            ),
                                        ],
                                        className="mb-2",
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Checklist(
                                                    id="global-options",
                                                    options=[
                                                        {"label": "Use log(X) in regression", "value": "logx"},
                                                        {"label": "Show regression line", "value": "reg"},
                                                    ],
                                                    value=["logx", "reg"],
                                                ),
                                                md=12,
                                            ),
                                            dbc.Col(
                                                [
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
                                                md=12,
                                            ),
                                        ],
                                        className="mb-2",
                                    ),
                                    dcc.Graph(
                                        id="global-scatter",
                                        config={"displayModeBar": True},
                                        style={"height": "520px"},
                                    ),
                                ]
                            ),
                        ],
                        className="h-100",
                    ),
                    md=6,
                ),

                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Indicator correlations"),
                            dbc.CardBody(
                                dcc.Graph(
                                    id="global-corr-heatmap",
                                    figure=build_correlation_heatmap(DF, CORR_COLS),
                                    style={"height": "520px"},
                                ),
                            ),
                        ],
                        className="h-100",
                    ),
                    md=6,
                ),
            ],
            className="mb-4",
        ),

        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("🏆 Global Leaderboard"),
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Metric"),
                                        dcc.Dropdown(
                                            id="leaderboard-metric",
                                            options=[{"label": m.replace('_', ' ').title(), "value": m} for m in LEADERBOARD_METRICS],
                                            value=DEFAULT_LEADERBOARD_METRIC,
                                            clearable=False,
                                        ),
                                    ], md=4),
                                    dbc.Col([
                                        dbc.Label("Top/Bottom N"),
                                        dcc.Slider(
                                            id="ranking-top-n",
                                            min=20,
                                            max=100,
                                            step=10,
                                            value=50,
                                            marks={20: "20", 50: "50", 100: "100"},
                                        ),
                                    ], md=4),
                                    dbc.Col([
                                        dbc.Checklist(
                                            id="show-bottom",
                                            options=[{"label": "Show BOTTOM performers", "value": "bottom"}],
                                            value=[],
                                        ),
                                    ], md=4),
                                ], className="mb-3"),
                                
                                dcc.Graph(
                                    id="global-ranking",
                                    figure=build_global_ranking(DF, DEFAULT_LEADERBOARD_METRIC, 50),
                                    style={"height": "600px"},
                                    config={"displayModeBar": True},
                                ),
                            ])
                        ],
                        className="h-100",
                    ),
                    md=12,
                ),
            ],
            className="mb-4",
        ),
    ],
    fluid=True,
)

# Existing callbacks (unchanged)
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

@callback(
    Output("global-ranking", "figure"),
    Input("leaderboard-metric", "value"),
    Input("ranking-top-n", "value"),
    Input("show-bottom", "value")
)
def update_global_ranking(metric: str, top_n: int, show_bottom: list):
    return build_global_ranking(DF, metric, top_n, "bottom" in show_bottom)
