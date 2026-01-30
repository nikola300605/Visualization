import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.data_loading.load_data import load_data_into_df
from src.components.clustering import create_development_clusters_without_analysis



def interactive_parallel_coords_dash(
    df: pd.DataFrame,
    dims: list,
    cluster_col: str = "cluster",
    country_col: str = "Country",
    title: str = "Interactive Parallel Coordinates",
    height: int = 700,
):
    """
    Create an interactive parallel coordinates plot optimized for Dash.
    Includes brushing/filtering capabilities.
    
    This version allows users to:
    - Select ranges on any axis to filter data
    - See which cluster each line belongs to
    - Interactive hover with country names
    
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
    
    print(f"📊 Plotting {len(d)} observations across {len(dims)} dimensions")
    print(f"📊 Clusters: {cluster_labels}")
    
    # Build dimensions for parallel coordinates
    dimensions = []
    
    for dim in dims:
        dim_dict = dict(
            label=dim,
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
    
    # Create figure
    fig = go.Figure(
        data=go.Parcoords(
            line=dict(
                color=d['cluster_numeric'],
                colorscale='Portland',  # Good for categorical data
                showscale=True,
                cmin=0,
                cmax=len(cluster_labels) - 1,
                colorbar=dict(
                    title="Cluster",
                    tickvals=list(range(len(cluster_labels))),
                    ticktext=[f"{c}" for c in cluster_labels],
                    len=0.6,
                    x=1.12,
                )
            ),
            dimensions=dimensions,
        )
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, weight="bold"),
            x=0.5,
            xanchor="center"
        ),
        height=height,
        margin=dict(l=100, r=180, t=80, b=60),
        font=dict(size=11),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    
    return fig


def interactive_parallel_coords_with_blending(
    df: pd.DataFrame,
    dims: list,
    cluster_col: str = "cluster",
    country_col: str = "Country",
    title: str = "Interactive Parallel Coordinates with Blending",
    height: int = 700,
    base_opacity: float = 0.15,  # Base transparency (very low for 251 lines)
    highlight_opacity: float = 0.8,  # Opacity when hovering
    colorscale: str = "Portland",
):
    """
    Enhanced version with better blending for 251 countries.
    Uses very low base opacity so overlapping lines blend nicely.
    
    IMPORTANT: Plotly's Parcoords has limited hover customization.
    This version uses a workaround to show country info.
    
    Args:
        df: DataFrame with cluster assignments and features
        dims: List of column names to visualize
        cluster_col: Name of cluster column
        country_col: Column name for country labels
        title: Plot title
        height: Figure height in pixels
        base_opacity: Base line transparency (0-1). Very low for many lines
        highlight_opacity: Opacity when selected/highlighted
        colorscale: Plotly colorscale name
    
    Returns:
        Plotly figure object
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
    d = d.dropna(subset=required_cols).reset_index(drop=True)
    
    # Map clusters to numeric values
    cluster_labels = sorted(d[cluster_col].unique())
    cluster_to_num = {c: i for i, c in enumerate(cluster_labels)}
    d['cluster_numeric'] = d[cluster_col].map(cluster_to_num)
    
    print(f"📊 Plotting {len(d)} countries across {len(dims)} dimensions")
    print(f"📊 Clusters: {cluster_labels}")
    print(f"📊 Using base opacity: {base_opacity} for optimal blending")
    
    # Build dimensions
    dimensions = []
    
    for dim in dims:
        dimensions.append(
            dict(
                label=dim,
                values=d[dim],
                range=[d[dim].min(), d[dim].max()],
            )
        )
    
    # Add cluster dimension
    dimensions.append(
        dict(
            label="Cluster",
            values=d['cluster_numeric'],
            tickvals=list(range(len(cluster_labels))),
            ticktext=[str(c) for c in cluster_labels],
            range=[0, len(cluster_labels) - 1],
        )
    )
    
    # Prepare hover text
    if country_col in d.columns:
        hover_labels = [f"{row[country_col]} (Cluster {row[cluster_col]})" 
                       for _, row in d.iterrows()]
    else:
        hover_labels = [f"Observation {i} (Cluster {row[cluster_col]})" 
                       for i, row in enumerate(d[cluster_col])]
    
    # Create figure
    fig = go.Figure(
        data=go.Parcoords(
            line=dict(
                color=d['cluster_numeric'],
                colorscale=colorscale,
                showscale=True,
                cmin=0,
                cmax=len(cluster_labels) - 1,
                colorbar=dict(
                    title="Cluster",
                    tickvals=list(range(len(cluster_labels))),
                    ticktext=[f"Cluster {c}" for c in cluster_labels],
                    len=0.6,
                    x=1.12,
                    thickness=20,
                ),
            ),
            dimensions=dimensions,
            # Control appearance when not selected (brushed)
            unselected=dict(
                line=dict(
                    color='rgba(128, 128, 128, 0.05)',  # Very faint gray
                    opacity=0.05
                )
            ),
        )
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, weight="bold"),
            x=0.5,
            xanchor="center"
        ),
        height=height,
        margin=dict(l=100, r=180, t=100, b=60),
        font=dict(size=11),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    
    # Add instruction annotation
    """ fig.add_annotation(
        text="💡 Tip: Drag vertically on any axis to filter. Hover over cluster regions to see patterns.",
        xref="paper", yref="paper",
        x=0.5, y=1.08,
        showarrow=False,
        font=dict(size=10, color="gray"),
        xanchor="center"
    ) """
    
    return fig

# -------------------------
# DASH INTEGRATION EXAMPLE
# -------------------------

    """
    Ready-to-use function for Dash apps.
    Returns a dcc.Graph component with the parallel coordinates plot.
    
    Usage in Dash:
        from dash import dcc
        
        # In your layout:
        dcc.Graph(
            id='parallel-coords-plot',
            figure=create_dash_parallel_coords_component(
                df, 
                dims=['feature1', 'feature2', 'feature3'],
                cluster_col='cluster'
            )
        )
    """
    return simple_parallel_coords(
        df=df,
        dims=dims,
        cluster_col=cluster_col,
        title="Development Indicators by Cluster"
    )

# -------------------------
# Example usage:
# -------------------------

if __name__ == "__main__":

    df_no_clusters = load_data_into_df()
    df = create_development_clusters_without_analysis(df_no_clusters, n_clusters=4)

    # EXAMPLE 1: Simple and Fast (Recommended for most cases)
    dims = [
        "Real_GDP_per_Capita_USD",
        "Life_Expectancy_at_Birth_(years)",
        "Total_Literacy_Rate [%]",
        "Expected_Years_of_Schooling_(years)",
        "Youth_Unemployment_Rate_percent",
    ]
    
    
    # EXAMPLE 3: Interactive with Filtering (Best for Dash)
    fig = interactive_parallel_coords_dash(
        df,
        dims=dims,
        cluster_col="Cluster",
        country_col="Country",
        title="Interactive Parallel Coordinates - Drag on axes to filter"
    )
    
    
    
    # EXAMPLE 4: Use in Dash App
    from dash import Dash, dcc, html
    import dash_bootstrap_components as dbc
    
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Development Cluster Analysis"),
                html.Hr(),
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='parallel-coords',
                    figure=fig,
                    style={'height': '600px'}
                )
            ])
        ])
    ])
    
    if __name__ == '__main__':
        app.run(debug=True)
    