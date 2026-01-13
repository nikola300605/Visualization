import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Output, Input, State, ctx
from src.data_loading.load_data import load_data_into_df
import numpy as np

df = load_data_into_df()


DEFAULT_FILTERS = {
    
}

def tab_layout():
    return dbc.Row(
        [ 
            dcc.Store(
                id = "filters-store",
                storage_type="memory",
            ),
            dbc.Col(
                [
                    dbc.Tabs(
                        [
                            dbc.Tab(label="Views", tab_id="tab-views"),
                            dbc.Tab(label="Filter", tab_id="tab-filter"),
                        ],
                        id="tabs",
                        active_tab="tab-filter",
                    ),
                ],
                width=8,
                id="tab-col"
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="country-dropdown",
                    options=[{"label": c, "value": c} for c in sorted(df["Country"].dropna().unique())],
                    className="dbc",
                ),
                width=4,
                className="mt-4",
                style={},
                id="dropdown-col"
            ),
            dbc.Col(
                dbc.ButtonGroup(
                    [
                        dbc.Button("Activate Filters", color="success", id="activate-button"),
                        dbc.Button("Reset Filters", color="danger", id="reset-button")
                    ],
                ),
                width=4,
                style = {},
                id="button-col",
                className="d-flex justify-content-end",
            ),
            dbc.Col(
                [
                    html.Div(views_content(), id="views-tab", style={"display": "none"}, className="mt-4"),
                    html.Div(filter_content(), id="filter-tab", style={"display": "none"}, className="mt-4"),
                ],
                width = 12,
                align="center"
            )
        ],
        justify="between"
    )



def views_content():
    return dbc.Row(
        [
            dbc.Col(
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
                width=8,
            ),
            dbc.Col(
                dbc.RadioItems(
                    id="views-radioitems",
                    options=[],          # filled by callback
                    value=None,          # set by callback
                    inline=True,
                ),
                width=12,
            )
        ],
        justify="start"
    )

def filter_content():

    economic_filters= dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Label("GDP per Capita Range (USD)", className="ps-4 pe-4"),
                    dcc.RangeSlider(
                        min = np.floor(df["Real_GDP_per_Capita_USD"].min()/5000)*5000,
                        max = np.ceil(df["Real_GDP_per_Capita_USD"].max()/5000)*5000,
                        step = 10000,
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False,
                        id = "Real_GDP_per_Capita_USD",
                        value = [
                            np.floor(df["Real_GDP_per_Capita_USD"].min()/5000)*5000,
                            np.ceil(df["Real_GDP_per_Capita_USD"].max()/5000)*5000
                        ]
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            ),
            dbc.Col(
                [
                    dbc.Label("Percent of Population below Poverty Line", className="ps-4 pe-4"),
                    dcc.Slider(
                        min = 0,
                        max = 100,
                        step = None,
                        marks = {i: f'{i}%' for i in range(0, 101, 10)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        id="Population_Below_Poverty_Line_percent",
                        value = 0
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            ),
            dbc.Col(
                [
                    dbc.Label("Unemployment Rate", className="ps-4 pe-4"),
                    dcc.Slider(
                        min = 0,
                        max = 100,
                        step = None,
                        marks = {i: f'{i}%' for i in range(0, 101, 10)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        id = "Unemployment_Rate_percent",
                        value = 0
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            ),
            dbc.Col(
                [
                    dbc.Label("Public debt (% of GDP)", className="ps-4 pe-4"),
                    dcc.Slider(
                        min = np.floor(df['Public_Debt_percent_of_GDP'].min()/20)*20,
                        max = np.ceil(df['Public_Debt_percent_of_GDP'].max()/20)*20,
                        step = None,
                        marks = {i: f'{i}%' for i in range(
                            int(np.floor(df['Public_Debt_percent_of_GDP'].min()/20)*20),
                            int(np.ceil(df['Public_Debt_percent_of_GDP'].max()/20)*20) + 1,
                            20
                        )},
                        tooltip={"placement": "bottom", "always_visible": True},
                        id="Public_Debt_percent_of_GDP",
                        value = np.floor(df['Public_Debt_percent_of_GDP'].min()/20)*20
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            )
        ]
    )

    human_filters = dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Label("Literacy Rate", className="ps-4 pe-4"),
                    dcc.Slider(
                        min = 0,
                        max = 100,
                        step = None,
                        marks = {i: f'{i}%' for i in range(0, 101, 10)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        id = "Total_Literacy_Rate [%]",
                        value = 0
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            ),
            dbc.Col(
                [
                    dbc.Label("Youth Unemployment Rate", className="ps-4 pe-4"),
                    dcc.Slider(
                        min = 0,
                        max = 100,
                        step = None,
                        marks = {i: f'{i}%' for i in range(0, 101, 10)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        id="Youth_Unemployment_Rate_percent",
                        value = 0
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            ),
            dbc.Col(
                [
                    dbc.Label("Expected Years Of Schooling", className="ps-4 pe-4"),
                    dcc.RangeSlider(
                        min = np.floor(df['Expected_Years_of_Schooling_(years)'].min()/5)*5,
                        max = np.ceil(df['Expected_Years_of_Schooling_(years)'].max()/5)*5,
                        step = 5,
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False,
                        id="Expected_Years_of_Schooling_(years)",
                        value = [
                            np.floor(df['Expected_Years_of_Schooling_(years)'].min()/5)*5,
                            np.ceil(df['Expected_Years_of_Schooling_(years)'].max()/5)*5
                        ]
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            ),
            dbc.Col(
                [
                    dbc.Label("Human Development Index", className="ps-4 pe-4"),
                    dcc.RangeSlider(
                        min = np.round(np.floor(df['Human_Development_Index_(value)'].min() / 0.1) * 0.1, 2),
                        max = np.round(np.ceil(df['Human_Development_Index_(value)'].max() / 0.1) * 0.1, 2),
                        step = 0.1,
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False,
                        id = "Human_Development_Index_(value)",
                        value = [
                            np.round(np.floor(df['Human_Development_Index_(value)'].min() / 0.1) * 0.1, 2),
                            np.round(np.ceil(df['Human_Development_Index_(value)'].max() / 0.1) * 0.1, 2)
                        ]
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            )
        ]
    )

    demography_filters = dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Label("Median Age", className="ps-4 pe-4"),
                    dcc.RangeSlider(
                        min = np.int16(np.floor(df["Median_Age"].min() / 5) * 5),
                        max = np.int16(np.ceil(df["Median_Age"].max() / 5) * 5),
                        step = 5,
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False,
                        id="Median_Age",
                        value = [
                            np.int16(np.floor(df["Median_Age"].min() / 5) * 5),
                            np.int16(np.ceil(df["Median_Age"].max() / 5) * 5)
                        ]
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            ),
            dbc.Col(
                [
                    dbc.Label("Population Growth Rate", className="ps-4 pe-4"),
                    dcc.RangeSlider(
                        min = np.floor(df['Population_Growth_Rate_(percentage)'].min()),
                        max = np.ceil(df['Population_Growth_Rate_(percentage)'].max()),
                        step = 1,
                        marks = {i: f'{i}%' for i in range(
                            int(np.floor(df['Population_Growth_Rate_(percentage)'].min())),
                            int(np.ceil(df['Population_Growth_Rate_(percentage)'].max())) + 1,
                            1
                        )},
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross = False,
                        id="Population_Growth_Rate_(percentage)",
                        value = [
                            np.floor(df['Population_Growth_Rate_(percentage)'].min()),
                            np.ceil(df['Population_Growth_Rate_(percentage)'].max())
                        ]
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            ),
            dbc.Col(
                [
                    dbc.Label("Life Expectancy at Birth (years)", className="ps-4 pe-4"),
                    dcc.RangeSlider(
                        min = np.floor(df['Life_Expectancy_at_Birth_(years)'].min()/5)*5,
                        max = np.ceil(df['Life_Expectancy_at_Birth_(years)'].max()/5)*5,
                        step = 5,
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False,
                        id="Life_Expectancy_at_Birth_(years)",
                        value = [
                            np.floor(df['Life_Expectancy_at_Birth_(years)'].min()/5)*5,
                            np.ceil(df['Life_Expectancy_at_Birth_(years)'].max()/5)*5
                        ]
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            ),
            dbc.Col(
                [
                    dbc.Label("Net Migration Rate (per 1,000 population)", className="ps-4 pe-4"),
                    dcc.RangeSlider(
                        min = np.round(np.floor(df['Net_Migration_Rate_(per_1,000_population)'].min() / 5) * 5, 2),
                        max = np.round(np.ceil(df['Net_Migration_Rate_(per_1,000_population)'].max() / 5) * 5, 2),
                        step = 5,
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False,
                        id="Net_Migration_Rate_(per_1,000_population)",
                        value = [
                            np.round(np.floor(df['Net_Migration_Rate_(per_1,000_population)'].min() / 5) * 5, 2),
                            np.round(np.ceil(df['Net_Migration_Rate_(per_1,000_population)'].max() / 5) * 5, 2)
                        ]
                    )
                ],
                width=6,
                className="dbc mb-4 mt-4"
            )
        ]
    )

    infrastructure_filters = dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Label("Internet Penetration Rate", className="ps-4 pe-4"),
                    dcc.RangeSlider(
                        min = 0,
                        max = 100,
                        step = 5,
                        marks = {i: f'{i}%' for i in range(0, 101, 10)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False,
                        id="internet_penetration_rate",
                        value = [
                            0, 100
                        ]
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            ),
            dbc.Col(
                [
                    dbc.Label("Electricity Access (%)", className="ps-4 pe-4"),
                    dcc.RangeSlider(
                        min = 0,
                        max = 100,
                        step = 5,
                        marks = {i: f'{i}%' for i in range(0, 101, 10)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross = False,
                        id="electricity_access_percent",
                        value = [0, 100]
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            ),
            dbc.Col(
                [
                    dbc.Label("Population density", className="ps-4 pe-4"),
                    dcc.RangeSlider(
                        min = np.floor(df['population_density'].min()/20)*20,
                        max = np.ceil(df['population_density'].max()/20)*20,
                        #step = 20,
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False,
                        id="population_density",
                        value = [
                            np.floor(df['population_density'].min()/20)*20,
                            np.ceil(df['population_density'].max()/20)*20
                        ]
                    ),
                ],  
                width=6,
                className="dbc mb-4 mt-4"
            ),
            dbc.Col(
                [
                    dbc.Label("Arable land (% of total)", className="ps-4 pe-4"),
                    dcc.RangeSlider(
                        min = 0,
                        max = 100,
                        step = 5,
                        marks = {i: f'{i}%' for i in range(0, 101, 10)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False,
                        id="Arable_Land (%% of Total Agricultural Land)_%",
                        value = [0, 100]
                    ),
                ],
                width=6,
                className="dbc mb-4 mt-4"
            )
        ]
    )


    return dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Tabs(
                        [
                            dbc.Tab([economic_filters], label="Income & Economic Structure"),
                            dbc.Tab([human_filters], label="Human Capital & Societal Outcomes"),
                            dbc.Tab([demography_filters], label="Demography & Population Dynamics"),
                            dbc.Tab([infrastructure_filters], label="Infrastructure & Geography"),
                        ]
                    )
                ],
                width=12,
            )
        ],
        justify="start",
    )

@callback(
    Output("views-tab", "style"),
    Output("filter-tab", "style"),
    Output("dropdown-col", "style"),
    Output("button-col", "style"),
    Input("tabs", "active_tab"),
)
def show_tab(active_tab):
    return (
        {"display": "block"} if active_tab == "tab-views" else {"display": "none"},
        {"display": "block"} if active_tab == "tab-filter" else {"display": "none"},
        {"display": "block"} if active_tab == None or active_tab == "tab-views" else {"display" : "none"},
        {"display": "block"} if active_tab == "tab-filter" else {"display": "none"}
    )


@callback(
    Output("views-radioitems", "options"),
    Output("views-radioitems", "value"),
    Input("views-dropdown", "value"),
)
def update_views(selected_view):
    options_by_view = {
        "economy": [
            {"label": "Real GDP per capita", "value": "Real_GDP_per_Capita_USD"},
            {"label": "Total GDP (billion USD)", "value": "Real_GDP_PPP_billion_USD"},
            {"label": "Unemployment Rate", "value": "Unemployment_Rate_percent"},
            {"label": "Poverty Rate", "value": "Population_Below_Poverty_Line_percent"},
            {"label": "Public Debt (Percent GDP)", "value": "Public_Debt_percent_of_GDP"},
        ],
        "development": [
            {"label": "Human Development Index", "value": "Human_Development_Index_(value)"},
            {"label": "Literacy Rate", "value": "Total_Literacy_Rate [%]"},
            {"label": "Youth Unemployment", "value": "Youth_Unemployment_Rate [%]"},
            {"label": "Median Age", "value": "Median_Age"},
            {"label": "Life Expectancy at Birth", "value": "Life_Expectancy_at_Birth_(years)"},
        ],
        "demographics": [
            {"label": "Population Density", "value": "population_density"},
            {"label": "Population Growth Rate", "value": "Population_Growth_Rate_(percentage)"},
            {"label": "Fertility Rate", "value": "Total_Fertility_Rate"},
            {"label": "Arable Land (% of total)", "value": "Arable_Land (%% of Total Agricultural Land)_%"},
            {"label": "Irrigated Land (% of total agricultural)", "value": "irrigated_land_percent"},
        ],
        "infrastructure": [
            {"label": "Internet Penetration Rate", "value": "internet_penetration_rate"},
            {"label": "Electricity Access Rate", "value": "electricity_access_percent"},
            {"label": "Road Density", "value": "road_density_log"},
            {"label": "Broadband Subscriptions", "value": "broadband_fixed_subscriptions_rate"},
        ],
    }

    opts = options_by_view.get(selected_view, [])
    default_value = None
    return opts, default_value

@callback(
    Output("filter-store", "data"),
    Input("activate-button", "n_clicks"),
    Input("reset-button", "n_clicks"),
    State("Real_GDP_per_Capita_USD", "value"),
    State("Population_Below_Poverty_Line_percent", "value"),
    State("Unemployment_Rate_percent", "value"),
    State("Public_Debt_percent_of_GDP", "value"),
    State("Total_Literacy_Rate [%]", "value"),
    State("Youth_Unemployment_Rate_percent", "value"),
    State("Expected_Years_of_Schooling_(years)", "value"),
    State("Human_Development_Index_(value)", "value"),
    State("Median_Age", "value"),
    State("Population_Growth_Rate_(percentage)", "value"),
    State("Life_Expectancy_at_Birth_(years)", "value"),
    State("Net_Migration_Rate_(per_1,000_population)", "value"),
    State("internet_penetration_rate", "value"),
    State("electricity_access_percent", "value"),
    State("population_density", "value"),
    State("Arable_Land (%% of Total Agricultural Land)_%", "value")
)   
def apply_reset_filter(
    activate_clicks,
    reset_clicks,
    gdp_per_capita,
    below_poverty_rate,
    unemployment_rate,
    public_debt,
    literacy_rate,
    youth_unemployment_rate,
    exp_year_schooling,
    hdi,
    median_age,
    population_growth,
    life_expectancy,
    migration_rate,
    internet_pen,
    elec_access,
    population_density,
    arable_land_perc
):
    
    if ctx.triggered_id == None:
        return DEFAULT_FILTERS

    if ctx.triggered_id == "reset-button":
        return DEFAULT_FILTERS
    
    if ctx.triggered_id == "activate_button":
        return {
            ...
        }



