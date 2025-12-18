from dash import Dash
import dash_bootstrap_components as dbc
from src.pages.main_layout import get_layout
from dash_bootstrap_templates import load_figure_template
import pathlib
#At first we set up for single page apps, can be later extended to multi page apps

load_figure_template("darkly")
dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")

local_css_path = pathlib.Path(__file__).parent.parent/'assets'/'style.css'
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME, dbc_css, local_css_path], suppress_callback_exceptions=True,
           use_pages=True)


server = app.server



app.layout = get_layout()
if __name__ == "__main__":
    app.run(debug=True)

