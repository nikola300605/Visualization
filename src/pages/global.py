import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, callback, Input, Output
from src.data_loading.load_data import load_data_into_df
from src.components.filter import get_label
import plotly.express as px

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

PARALLEL_COORD_COLS = [
    "Real_GDP_per_Capita_USD",
    "Life_Expectancy_at_Birth_(years)",
    "Expected_Years_of_Schooling_(years)",
    "Population_Below_Poverty_Line_percent",
    "Median_Age",
    "Human_Development_Index_(value)",
    "Total_Fertility_Rate",
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
                f"{get_label(x_col)}: %{{x}}<br>"
                f"{get_label(y_col)}: %{{y}}<br>"
                "Expected: %{customdata[1]:.2f}<br>"
                "Residual: %{customdata[2]:.2f}<extra></extra>"
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
            marker=dict(size=10, opacity = 0.5),
            text=under["Country"],
            textposition="top center",
            textfont=dict(size=10, weight=300),
            customdata=np.stack([under["Country"], under["predicted"], under["residual"]], axis=1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                f"{get_label(x_col)}: %{{x}}<br>"
                f"{get_label(y_col)}: %{{y}}<br>"
                "Expected: %{customdata[1]:.2f}<br>"
                "Residual: %{customdata[2]:.2f}<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=over[x_col],
            y=over[y_col],
            mode="markers+text",
            name="Over-performing",
            marker=dict(size=10, opacity = 0.5),
            text=over["Country"],
            textposition="top center",
            textfont=dict(size=10, weight=300),
            customdata=np.stack([over["Country"], over["predicted"], over["residual"]], axis=1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                f"{get_label(x_col)}: %{{x}}<br>"
                f"{get_label(y_col)}: %{{y}}<br>"   
                "Expected: %{customdata[1]:.2f}<br>"
                "Residual: %{customdata[2]:.2f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(
        text="Social vs Economic indicator",
        font=dict(size=18),
        x=0.5,),
        xaxis_title=get_label(x_col) if not use_log_x else f"{get_label(x_col)} (log used in model)",
        yaxis_title=get_label(y_col),
        legend_title="",
        margin=dict(l=10, r=10, t=55, b=10),
    )

    return fig

def build_correlation_heatmap(df: pd.DataFrame, cols: list[str]) -> go.Figure:
    data = df[cols].dropna()
    corr = data.corr()
    labels = [get_label(c) for c in corr.columns]


    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=labels,
            y=labels,
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

    fig.add_annotation(
    text="Click on tile to explore their relationship!",
    xref="paper", yref="paper",
    x=0.5, y=1.08,  # Centered above the plot
    showarrow=False,
    font=dict(size=12, color="white"),
    align="center"
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

def interactive_parallel_coords(
    df: pd.DataFrame,
    dims: list,
    cluster_col: str = "cluster",
    country_col: str = "Country",
    title: str = "Interactive Parallel Coordinates",
    height: int = 700,
):
    """
    Create an interactive parallel coordinates plot optimized for Dash.
    Enhanced version with improved visual styling and readability.
    
    Args:
        df: DataFrame with cluster assignments and features
        dims: List of column names to visualize
        cluster_col: Name of cluster column
        country_col: Column name for hover labels
        title: Plot title
        height: Figure height in pixels
    
    Returns:
        Plotly figure object ready for Dash
    """
    
    # Validate columns
    missing_cols = [c for c in [cluster_col, *dims] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in df: {missing_cols}")
    
    # Clean data
    d = df.copy()
    
    # Ensure dims are numeric
    for col in dims:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    
    # Drop rows with missing values
    required_cols = [cluster_col, *dims]
    if country_col in d.columns:
        required_cols.append(country_col)
    d = d.dropna(subset=required_cols)
    
    # Map clusters to numeric values
    cluster_labels = sorted(d[cluster_col].unique())
    cluster_to_num = {c: i for i, c in enumerate(cluster_labels)}
    d['cluster_numeric'] = d[cluster_col].map(cluster_to_num)

    # Build dimensions for parallel coordinates
    dimensions = []
    
    for dim in dims:
        dim_dict = dict(
            label=get_label(dim),
            values=d[dim],
            range=[d[dim].min(), d[dim].max()],
        )
        dimensions.append(dim_dict)
    
    # Add cluster as a constraintrange dimension (for filtering)
    dimensions.append(
        dict(
            label="Cluster",
            values=d['cluster_numeric'],
            tickvals=list(range(len(cluster_labels))),
            ticktext=[str(c) for c in cluster_labels],
            range=[0, len(cluster_labels) - 1],
        )
    )
    
    # Create figure with enhanced styling
    fig = go.Figure(
        data=go.Parcoords(
            line=dict(
                color=d['cluster_numeric'],
                colorscale = ["rgba(27,158,119,1)", "rgba(217,95,2,1)", "rgba(117,112,179,1)", "rgba(231,41,138,1)"],
                showscale=True,
                cmin=0,
                cmax=len(cluster_labels) - 1,
                colorbar=dict(
                    title=dict(
                        text="Cluster",
                        font=dict(size=14, color='white')
                    ),
                    tickvals=list(range(len(cluster_labels))),
                    ticktext=[f"{c}" for c in cluster_labels],
                    tickfont=dict(size=12, color='white', family='Arial'),
                    x=1.12
                )
            ),
            dimensions=dimensions,
            # Enhanced label styling
            labelfont=dict(
                size=10,
                color='white'
            ),
            # Enhanced tick styling
            tickfont=dict(
                size=11,
                color='rgba(255, 255, 255, 0.9)',
                family='Arial'
            ),
            # Stronger axis lines
            rangefont=dict(
                size=11,
                color='white'
            ),
        )
    )
    
    # Update layout with enhanced styling
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=20, color='white'),
            x=0.02,
            xanchor="left",
            y=1,
            yanchor="top"
        ),
        height=height,
        margin=dict(l=120, r=200, t=100, b=80),
        font=dict(size=12, color='white'),
    )
    
    # Add custom axis styling through shapes and annotations
    # This makes the axes more visible
    shapes = []
    annotations = []
    
    # Calculate x positions for each dimension
    n_dims = len(dimensions)
    x_positions = [i / (n_dims - 1) for i in range(n_dims)]
    
    # Add stronger vertical lines for each axis
    for i, x_pos in enumerate(x_positions):
        shapes.append(
            dict(
                type='line',
                xref='paper',
                yref='paper',
                x0=x_pos,
                y0=0,
                x1=x_pos,
                y1=1,
                line=dict(
                    color='rgba(255, 255, 255, 0.4)',
                    width=2.5
                )
            )
        )
    
    fig.update_layout(shapes=shapes)

    fig.add_annotation(
    text="Filter by clicking and dragging on axes!",
    xref="paper", yref="paper",
    x=0.5, y=1.2,  # Centered above the plot
    showarrow=False,
    font=dict(size=12, color="white"),
    align="center"
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
                                                        options=[{"label": get_label(c), "value": c} for c in ECON_COLS],
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
                                                        options=[{"label": get_label(c), "value": c} for c in SOCIAL_COLS],
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
                                [
                                    dcc.Graph(
                                        id="global-corr-heatmap",
                                        figure=build_correlation_heatmap(DF, CORR_COLS),
                                        style={"height": "520px"},
                                        clickData=None,
                                    ),
                                    dcc.Graph(
                                        id = "scatterplot-correlation",
                                        figure = px.scatter(),
                                        style={"height": "400px"},
                                        className="dbc"
                                    )
                                ]
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

        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("🌐 Parallel Coordinates of Development Indicators"),
                            dbc.CardBody(
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Graph(
                                                id="global-parallel-coords",
                                                figure=interactive_parallel_coords(
                                                    DF,
                                                    dims=PARALLEL_COORD_COLS,
                                                    cluster_col="Cluster",
                                                    country_col="Country",
                                                    title="Development Indicators by Cluster",
                                                    height=500,
                                                ),
                                                className="dbc",
                                                style={"height": "550px"},
                                                config={"displayModeBar": True},
                                            ),
                                            md=12
                                        )
                                    ]
                                )
                            ),
                        ],
                        className="h-100",
                    ),
                    md=12,
                    width = 12
                ),
            ]
        )
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



@callback(
    Output("scatterplot-correlation", "figure"),
    Input("global-corr-heatmap", "clickData"),
    prevent_initial_call=True,
)

def create_update_scatterplot(clickData):
    if clickData is None:
        return dash.no_update

    x_pretty = clickData['points'][0]['x']
    y_pretty = clickData['points'][0]['y']

    # Map pretty labels back to DataFrame columns
    col_mapping = {get_label(c): c for c in DF.columns}

    if x_pretty not in col_mapping or y_pretty not in col_mapping:
        return dash.no_update

    x_col = col_mapping[x_pretty]
    y_col = col_mapping[y_pretty]

    fig = px.scatter(
        DF,
        x=x_col,
        y=y_col,
        hover_data=['Country'],
    )

    fig.update_xaxes(
        title=get_label(x_col)
    )

    fig.update_yaxes(
        title=get_label(y_col)
    )

    fig.update_layout(
        title=dict(
            text=f"Scatterplot: {get_label(x_col)} vs {get_label(y_col)}",
            font=dict(size=18),
            x=0.5,
        )
    )

    return fig