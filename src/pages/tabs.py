import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Output, Input, State

def tab_layout():
    tabs = html.Div(
        [
            dbc.Tabs(
            [
                dbc.Tab(label="Views", tab_id="tab-views"),
                dbc.Tab(label="Filter", tab_id="tab-filter"),
            ],
            id="tabs",
            active_tab="tab-views",
            ),
            html.Div(id="tab-content",className="mt-4"),
        ]
    )

    return tabs



def views_content():
    return dbc.Container(
        dbc.Row(
            [
                dcc.Dropdown(
                    options=[
                        {'label': 'Economic Perforamnce & Structural Conditions', 'value': 'economy'},
                        {'label': 'Human development & Capabilities', 'value': 'development'},
                        {'label': 'Demography, Land & Resource Pressure', 'value': 'demographics'},
                        {'label': 'Infrastructure, Technology & Access', 'value': 'infrastructure'},
                    ],
                    multi=False,
                    value='economy',
                    id='views-dropdown',
                    className="dbc mb-4"
                ),
                dbc.Col(
                    html.Div(id="views-inner"),
                    width=12
                )
            ]
        )
    )

def filter_content():
    return dbc.Container(
        dbc.Row(
            [
                dbc.Col(
                    [   
                    dbc.Label("Select Region:", html_for="region-filter-dropdown", className="form-label"),
                    dcc.Dropdown(
                        options = [
                            {'label': 'All Regions', 'value': 'all'},
                            {'label': 'Europe', 'value': 'europe'},
                            {'label': 'Asia', 'value': 'asia'},
                            {'label': 'Africa', 'value': 'africa'},
                            {'label': 'North America', 'value': 'north_america'},
                            {'label': 'South America', 'value': 'south_america'},
                            {'label': 'Oceania', 'value': 'oceania'},
                            {'label': 'Antarctica', 'value': 'antarctica'},
                        ],
                        id = "region-filter-dropdown",
                        className="dbc"
                    )
                    ],
                    width=4
                ),

            ]
        )
    )


@callback(
    Output(component_id="tab-content", component_property="children"),
    Input(component_id="tabs", component_property="active_tab")
)
def switch_tab(active_tab):
    if active_tab == "tab-views":
        return views_content()
    elif active_tab == "tab-filter":
        return filter_content()
    return  html.P("This shouldn't ever be displayed...")


@callback(
    Output(component_id="views-inner", component_property="children"),
    Input(component_id="views-dropdown", component_property="value")
)

def update_views(selected_view):

    economy_buttons = dbc.RadioItems(
        id="views-radioitems",
        options=[
            {"label": "Real GDP per capita", "value": "Real_GDP_per_Capita_USD"},
            {"label": "Total GDP", "value": "Real_GDP_PPP_billion_USD"},
            {"label": "Unemployment Rate", "value": "Unemployment_Rate_percent"},
            {"label": "Poverty Rate", "value": "Population_Below_Poverty_Line_percent"},
            {"label": "Public Debt (Percent GDP)", "value": "Public_Debt_percent_of_GDP"},
        ],
        inline=True,
    )

    development_buttons = dbc.RadioItems(
        id="views-radioitems",
        options=[
            {"label": "Literacy Rate", "value": "Total_Literacy_Rate"},
            {"label": "Youth Unemployment", "value": "Youth_Unemployment_Rate"},
            {"label": "Median Age", "value": "Median_Age"},
        ],
        inline=True,
    )

    demographics_buttons = dbc.RadioItems(
        id="views-radioitems",
        options=[
            {"label": "Population Density", "value": "population_density"},
            {"label": "Population Growth Rate", "value": "Population_Growth_Rate"},
            {"label": "Fertility Rate", "value": "Total_Fertility_Rate"},
            {"label": "Arable Land (% of total)", "value": "Arable_Land (%% of Total Agricultural Land)"},
        ],
        inline=True,
    )

    infrastructure_buttons = dbc.RadioItems(
        id="views-radioitems",
        options=[
            {"label": "Internet Penetration Rate", "value": "internet_penetration_rate"},
            {"label": "Electricity Access Rate", "value": "electricity_access_percent"},
            {"label": "Road Density", "value": "road_density"},
            {"label": "Broadband Subscriptions", "value": "broadband_fixed_subscriptions_total"},
        ],
        inline=True,
    )



    if selected_view == 'development':
        return development_buttons
    elif selected_view == 'economy':
        return economy_buttons
    elif selected_view == 'demographics':
        return demographics_buttons
    elif selected_view == 'infrastructure':
        return infrastructure_buttons
    return html.P("Select a view to see options.")
