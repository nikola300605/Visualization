import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import State, html, dcc, callback, Input, Output, ctx
import urllib.parse
import numpy as np

from src.components.map import generate_choropleth, make_base_map, generate_filter_based_chloropeth
from src.components.tabs import tab_layout, DEFAULT_FILTERS, _norm
from src.data_loading.load_data import load_data_into_df
from src.components.filter import filter_df, get_label

dash.register_page(__name__, path="/", name="Home", order=0)

df = load_data_into_df()
cols_to_ignore = ["Country", "ISO3"]
mask_empty = df.drop(columns=cols_to_ignore).isna().all(axis=1)
df_empty = df[mask_empty]
df_nonempty = df[~mask_empty]

fig_map = generate_choropleth()

layout = dbc.Container(
    dbc.Row([
        dcc.Store(id="filters-store", storage_type="memory"),
        dcc.Store(id="current-view-metric-store", storage_type="memory"),
        # Toast for filter-limit notifications (top-right)
        dbc.Toast(
            id="filter-limit-toast",
            header="Filter Limit",
            children="",
            icon="warning",
            duration=4000,
            is_open=False,
            dismissable=True,
            style={"position": "fixed", "top": 10, "right": 10, "zIndex": 2000},
        ),
        dbc.Col(dcc.Graph(id="graph", figure=fig_map, className="dbc"),
                width=12, className="mb-4"),
        
        dbc.Col(
            children =[
                html.Div([
                    html.Small("Filters: ", className="text-muted"),
                    html.Div(children = [],id="active-filters-display", className="d-inline-flex gap-2")
                ], 
                className="mt-2 mb-3 d-flex justify-content-center align-items-center gap-2")
            ],
            width = 12,
        ),

        dbc.Col(
            dbc.Alert(id="filter-warning", is_open=False, color="danger"),
            width=12,
            className="mt-2"
        ),

        dbc.Col(tab_layout(), width=12, className="mt-4"),
    ]),
    fluid=True
)

@callback(
    Output("graph", "figure", allow_duplicate=True),
    Output("current-view-metric-store", "data", allow_duplicate=True),
    Output("filters-store", "data", allow_duplicate=True),
    Output("active-filters-display", "children", allow_duplicate=True),
    Output("Real_GDP_per_Capita_USD", "value", allow_duplicate=True),
    Output("Population_Below_Poverty_Line_percent", "value", allow_duplicate=True),
    Output("Unemployment_Rate_percent", "value", allow_duplicate=True),
    Output("Public_Debt_percent_of_GDP", "value", allow_duplicate=True),
    Output("Total_Literacy_Rate [%]", "value", allow_duplicate=True),
    Output("Youth_Unemployment_Rate_percent", "value", allow_duplicate=True),
    Output("Expected_Years_of_Schooling_(years)", "value", allow_duplicate=True),
    Output("Human_Development_Index_(value)", "value", allow_duplicate=True),
    Output("Median_Age", "value", allow_duplicate=True),
    Output("Population_Growth_Rate_(percentage)", "value", allow_duplicate=True),
    Output("Life_Expectancy_at_Birth_(years)", "value", allow_duplicate=True),
    Output("Net_Migration_Rate_(per_1,000_population)", "value", allow_duplicate=True),
    Output("internet_penetration_rate", "value", allow_duplicate=True),
    Output("electricity_access_percent", "value", allow_duplicate=True),
    Output("Agricultural_Land_%", "value", allow_duplicate=True),
    Output("Arable_Land (%% of Total Agricultural Land)_%", "value", allow_duplicate=True),
    Input("views-radioitems", "value"),
    prevent_initial_call=True,
)
def update_graph(selected_column):
    # Reset filters when changing views
    reset_store = {
        "DEFAULT_FILTERS": {k: _norm(v) for k, v in DEFAULT_FILTERS.items()},
        "ACTIVE_FILTERS": None
    }
    
    # Prepare reset slider values
    slider_reset = (
        DEFAULT_FILTERS["Real_GDP_per_Capita_USD"],
        DEFAULT_FILTERS["Population_Below_Poverty_Line_percent"],
        DEFAULT_FILTERS["Unemployment_Rate_percent"],
        DEFAULT_FILTERS["Public_Debt_percent_of_GDP"],
        DEFAULT_FILTERS["Total_Literacy_Rate [%]"],
        DEFAULT_FILTERS["Youth_Unemployment_Rate_percent"],
        DEFAULT_FILTERS["Expected_Years_of_Schooling_(years)"],
        DEFAULT_FILTERS["Human_Development_Index_(value)"],
        DEFAULT_FILTERS["Median_Age"],
        DEFAULT_FILTERS["Population_Growth_Rate_(percentage)"],
        DEFAULT_FILTERS["Life_Expectancy_at_Birth_(years)"],
        DEFAULT_FILTERS["Net_Migration_Rate_(per_1,000_population)"],
        DEFAULT_FILTERS["internet_penetration_rate"],
        DEFAULT_FILTERS["electricity_access_percent"],
        DEFAULT_FILTERS["Agricultural_Land_%"],
        DEFAULT_FILTERS["Arable_Land (%% of Total Agricultural Land)_%"],
    )
    
    if selected_column is None or selected_column not in df.columns:
        return fig_map, None, reset_store, "", *slider_reset

    fig = make_base_map()

    if selected_column == 'Real_GDP_PPP_billion_USD_log':
        tick_vals = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]
        tick_text = [f"${10**v:,.0f}B" if 10**v < 1000 else f"${10**v/1000:,.1f}T" for v in tick_vals]

        fig.add_choropleth(
            locations=df_nonempty["ISO3"],
            z=df_nonempty[selected_column],
            colorscale=px.colors.sequential.Plasma,
            customdata=np.stack([df_nonempty["Real_GDP_PPP_billion_USD"]], axis=-1),
            hovertemplate=(
                "<b>%{location}</b><br>"
                "GDP (PPP): $%{customdata[0]:,.0f}B<br>"
                "<extra></extra>"
            ),
            showscale=True,
            colorbar=dict(len=0.75,
                title='GDP (PPP, billion USD)<br><sub>colors use log scale</sub>',
                x=0.9,
                tickvals = tick_vals,
                ticktext = tick_text)
        )
    elif selected_column == 'population_density_log':

        tick_vals = [-1, 0, 1, 2, 3, 4]
        tick_text = [f"{10**v:,.0f}" if 10**v < 1000 else f"{10**v/1000:,.1f}K" for v in tick_vals]

        fig.add_choropleth(
            locations=df_nonempty["ISO3"],
            z=df_nonempty[selected_column],
            colorscale=px.colors.sequential.Plasma,
            customdata=np.stack([df_nonempty["population_density"]], axis=-1),
            hovertemplate=(
                "<b>%{location}</b><br>"
                "Population Density: %{customdata[0]:,.2f}<br>"
                "<extra></extra>"
            ),
            showscale=True,
            colorbar=dict(len=0.75,
                title='Population Density (log)<br><sub>colors use log scale</sub>',
                x=0.9,
                tickvals = tick_vals,
                ticktext = tick_text)
        )
    
    elif selected_column == 'road_density_log':
        tick_vals = [-1, 0, 1, 2]
        tick_text = [f"{10**v:,.2f}" if 10**v < 1000 else f"{10**v/1000:,.2f}K" for v in tick_vals]

        fig.add_choropleth(
            locations=df_nonempty["ISO3"],
            z=df_nonempty[selected_column],
            colorscale=px.colors.sequential.Plasma,
            customdata=np.stack([df_nonempty["road_density"]], axis=-1),
            hovertemplate=(
                "<b>%{location}</b><br>"
                "Road Density: %{customdata[0]:,.2f} km of road per km^2<br>"
                "<extra></extra>"
            ),
            showscale=True,
            colorbar=dict(len=0.75,
                title='Road Density (log)<br><sub>colors use log scale</sub>',
                x=0.9,
                tickvals = tick_vals,
                ticktext = tick_text)
        )

    elif selected_column == 'Real_GDP_per_Capita_USD_log':
        tick_vals = [3, 3.5, 4, 4.5, 5]
        tick_text = [f"${10**v:,.0f}" if 10**v < 1000 else f"${10**v/1000:,.1f}K" for v in tick_vals]

        fig.add_choropleth(
            locations=df_nonempty["ISO3"],
            z=df_nonempty[selected_column],
            colorscale=px.colors.sequential.Plasma,
            customdata=np.stack([df_nonempty["Real_GDP_per_Capita_USD"]], axis=-1),
            hovertemplate=(
                "<b>%{location}</b><br>"
                "GDP per Capita: %{customdata[0]:,.0f} USD<br>"
                "<extra></extra>"
            ),
            showscale=True,
            colorbar=dict(len=0.75,
                title='Real GDP per Capita (USD)<br><sub>colors use log scale</sub>',
                x=0.9,
                tickvals = tick_vals,
                ticktext = tick_text)
        )
    else:
        # Normal handling for all other columns
        fig.add_choropleth(
            locations=df_nonempty["ISO3"],
            z=df_nonempty[selected_column],
            colorscale=px.colors.sequential.Plasma,
            customdata=df_nonempty[["Country", selected_column]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "" + get_label(selected_column) + ": %{customdata[1]:,.2f}<br>"
                "<extra></extra>"
            ),
            showscale=True,
            colorbar=dict(
            title=dict(
                text = f"{get_label(selected_column)}",
                side = "top"
            ),
            x=0.9,
            tickfont=dict(size=12),
            len=0.75,  # Optional: makes the colorbar a bit shorter
            )
        )
        
    

    # Handle missing data (works for both cases)
    mask_empty_col = df_nonempty[selected_column].isna()
    df_empty_col = pd.concat([df_empty, df_nonempty[mask_empty_col]], ignore_index=True)

    fig.add_choropleth(
        locations=df_empty_col["ISO3"],
        z=[0] * len(df_empty_col),
        showscale=False,
        hovertext="No data available",
        hoverinfo="text",
        marker_line_width=0.8,
        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
        marker_line_color="#E4CFCF",
    )

    fig.update_layout(title=f"{selected_column.replace('_', ' ').title()} by Country")
    return fig, selected_column, reset_store, "", *slider_reset



@callback(
    Output("graph", "figure", allow_duplicate=True),
    Output("current-view-metric-store", "data", allow_duplicate=True),
    Output("views-radioitems", "value", allow_duplicate=True),
    Input("reset-views-button", "n_clicks"),
    prevent_initial_call=True,
)
def reset_view(n_clicks):
    if n_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update
    return fig_map, None, None

@callback(
    Output("graph", "figure", allow_duplicate=True),
    Output("active-filters-display", "children"),
    Output("filter-warning", "children"),
    Output("filter-warning", "is_open"),
    Output("filter-limit-toast", "children"),
    Output("filter-limit-toast", "is_open"),
    Input("filters-store", "data"),
    Input("reset-button", "n_clicks"),
    State("current-view-metric-store", "data"),
    prevent_initial_call=True,
)

def apply_filters(filters_data, n_clicks_reset, current_view_metric):

    cols_to_ignore = ["Country", "ISO3"]
    mask_empty = df.drop(columns=cols_to_ignore).isna().all(axis=1)
    df_empty = df[mask_empty]

    if ctx.triggered_id == "reset-button":
        return fig_map, "", "", False, "", False

    # Check for LIMIT_EXCEEDED first - show warning toast even if filters weren't applied
    if filters_data and "LIMIT_EXCEEDED" in filters_data and filters_data["LIMIT_EXCEEDED"].get("show"):
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            filters_data["LIMIT_EXCEEDED"].get("message", "Too many filters selected"),
            True,
        )

    # Store triggered (from activate-button)
    if not filters_data or "ACTIVE_FILTERS" not in filters_data or filters_data["ACTIVE_FILTERS"] is None:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )
    
    DEFAULT_FILTERS = filters_data["DEFAULT_FILTERS"]
    active_filters = filters_data["ACTIVE_FILTERS"]
    # Check for LIMIT_EXCEEDED message from tabs
    limit_info = filters_data.get("LIMIT_EXCEEDED") if filters_data else None
    toast_children = ""
    toast_open = False
    if limit_info and limit_info.get("show"):
        toast_children = limit_info.get("message", "Too many filters selected")
        toast_open = True
    
    df_nonempty_filtered, active_filters_dict, missing_by_filter = filter_df(df_nonempty, active_filters, DEFAULT_FILTERS)

    if df_nonempty_filtered.empty:
        return (
            dash.no_update,
            " ".join(f"{get_label(col)}" for col in active_filters_dict.keys()),
            "No countries match these filters",
            True,
            "",
            False,
        )

    if current_view_metric is None or current_view_metric not in df.columns:
        return (
            generate_filter_based_chloropeth(df_nonempty_filtered, active_filters_dict, missing_by_filter, df_empty),
            ", ".join(f"{get_label(col)}" for col in active_filters_dict.keys()),
            "",
            False,
            toast_children,
            toast_open,
        )

    fig = make_base_map()

    if current_view_metric == 'Real_GDP_PPP_billion_USD_log':
        tick_vals = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]
        tick_text = [f"${10**v:,.0f}B" if 10**v < 1000 else f"${10**v/1000:,.1f}T" for v in tick_vals]

        fig.add_choropleth(
            locations=df_nonempty_filtered["ISO3"],
            z=df_nonempty_filtered[current_view_metric],
            colorscale=px.colors.sequential.Plasma,
            customdata=np.stack([df_nonempty_filtered["Real_GDP_PPP_billion_USD"]], axis=-1),
            hovertemplate=(
                "<b>%{location}</b><br>"
                "GDP (PPP): $%{customdata[0]:,.0f}B<br>"
                "<extra></extra>"
            ),
            showscale=True,
            colorbar=dict(len=0.75,
                title='GDP (PPP, billion USD)<br><sub>colors use log scale</sub>',
                x=0.9,
                tickvals = tick_vals,
                ticktext = tick_text)
        )

    elif current_view_metric == 'population_density_log':

        tick_vals = [-1, 0, 1, 2, 3, 4]
        tick_text = [f"{10**v:,.0f}" if 10**v < 1000 else f"{10**v/1000:,.1f}K" for v in tick_vals]

        fig.add_choropleth(
            locations=df_nonempty_filtered["ISO3"],
            z=df_nonempty_filtered[current_view_metric],
            colorscale=px.colors.sequential.Plasma,
            customdata=np.stack([df_nonempty_filtered["population_density"]], axis=-1),
            hovertemplate=(
                "<b>%{location}</b><br>"
                "Population Density: %{customdata[0]:,.2f}<br>"
                "<extra></extra>"
            ),
            showscale=True,
            colorbar=dict(len=0.75,
                title='Population Density (log)<br><sub>colors use log scale</sub>',
                x=0.9,
                tickvals = tick_vals,
                ticktext = tick_text)
        )
    
    elif current_view_metric == 'road_density_log':
        tick_vals = [-1, 0, 1, 2]
        tick_text = [f"{10**v:,.2f}" if 10**v < 1000 else f"{10**v/1000:,.2f}K" for v in tick_vals]

        fig.add_choropleth(
            locations=df_nonempty_filtered["ISO3"],
            z=df_nonempty_filtered[current_view_metric],
            colorscale=px.colors.sequential.Plasma,
            customdata=np.stack([df_nonempty_filtered["road_density"]], axis=-1),
            hovertemplate=(
                "<b>%{location}</b><br>"
                "Road Density: %{customdata[0]:,.2f} km of road per km^2<br>"
                "<extra></extra>"
            ),
            showscale=True,
            colorbar=dict(len=0.75,
                title='Road Density (log)<br><sub>colors use log scale</sub>',
                x=0.9,
                tickvals = tick_vals,
                ticktext = tick_text)
        )

    elif current_view_metric == 'Real_GDP_per_Capita_USD_log':
        tick_vals = [3, 3.5, 4, 4.5, 5]
        tick_text = [f"${10**v:,.0f}" if 10**v < 1000 else f"${10**v/1000:,.1f}K" for v in tick_vals]

        fig.add_choropleth(
            locations=df_nonempty_filtered["ISO3"],
            z=df_nonempty_filtered[current_view_metric],
            colorscale=px.colors.sequential.Plasma,
            customdata=np.stack([df_nonempty_filtered["Real_GDP_per_Capita_USD"]], axis=-1),
            hovertemplate=(
                "<b>%{location}</b><br>"
                "GDP per Capita: %{customdata[0]:,.0f} USD<br>"
                "<extra></extra>"
            ),
            showscale=True,
            colorbar=dict(len=0.75,
                title='Real GDP per Capita (USD)<br><sub>colors use log scale</sub>',
                x=0.9,
                tickvals = tick_vals,
                ticktext = tick_text)
        )

    
    else:
        fig.add_choropleth(
            locations=df_nonempty_filtered["ISO3"],
            z=df_nonempty_filtered[current_view_metric],
            colorscale=px.colors.sequential.Plasma,
            customdata=df_nonempty[["Country", current_view_metric]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "" + get_label(current_view_metric) + ": %{customdata[1]:,.2f}<br>"
                "<extra></extra>"
            ),
            showscale=True,
            colorbar=dict(
            title=dict(
                text = f"{get_label(current_view_metric)}",
                side = "top"
            ),
            x=0.9,
            tickfont=dict(size=12),
            len=0.75,  # Optional: makes the colorbar a bit shorter
            )
        )

    fig.update_layout(title=f"{current_view_metric.replace('_', ' ').title()} by Country")

    return (
        fig,
        ", ".join(f"{get_label(col)}" for col in active_filters_dict.keys()),
        "",
        False,
        toast_children,
        toast_open,
    )

@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("url", "search",  allow_duplicate=True),
    Input("graph", "clickData"),
    prevent_initial_call=True,
)
def go_to_country(clickData):
    if not clickData:
        return dash.no_update, dash.no_update

    pts = clickData.get("points", [])
    if not pts:
        return dash.no_update, dash.no_update

    iso3 = pts[0].get("location")
    if not iso3:
        return dash.no_update, dash.no_update

    return "/country", f"?iso3={iso3}"

@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("url", "search", allow_duplicate=True),
    Input("country-dropdown", "value"),
    prevent_initial_call=True,
)
def go_to_country(value):
    if not value:
        return dash.no_update, dash.no_update

    if value is None:
        return dash.no_update, dash.no_update
    
    if value not in df["ISO3"].values:
        return dash.no_update, dash.no_update
    
    iso3 = value

    return "/country", f"?iso3={iso3}"

