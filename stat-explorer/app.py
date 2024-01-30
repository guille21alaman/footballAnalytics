from pathlib import Path

import pandas as pd
from modules.oldModules import data_view_server, data_view_ui, training_server, training_ui
from modules.compareStats import *

from shiny import App, Inputs, Outputs, Session, reactive, ui


app_ui = ui.page_fluid(
    ui.h1("Football Stat Explorer", align="center", margin="1em"),
    ui.page_navbar(
        compare_stats_ui("compareTab"),
    ),
    id="tabs",
)
    

def server(input: Inputs, output: Outputs, session: Session):
    compare_stats_server(id="compareTab")

app = App(app_ui, server)
