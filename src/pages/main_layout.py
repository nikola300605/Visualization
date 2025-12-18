import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

def Navbar():
    pages = sorted(dash.page_registry.values(), key=lambda p: p.get("order", 0))
    return dbc.NavbarSimple(
        brand="World explorer",
        children=[
            dbc.NavItem(dbc.NavLink(page["name"], href=page["relative_path"]))
            for page in pages
        ],
        color="primary",
        dark=True,
        class_name="mb-4"
    )

def get_layout():
    return dbc.Container(
        [
            Navbar(),
            dash.page_container,   # <-- where pages render
        ],
        fluid=True
    )