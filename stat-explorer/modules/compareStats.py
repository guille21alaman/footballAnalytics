import pandas as pd
import numpy as np
from shiny import Inputs, Outputs, Session, module, render, ui
from shinywidgets import *
from shiny.types import ImgData
import os
from bokeh.plotting import figure
from scipy.stats import linregress




@module.ui
def compare_stats_ui():
    return ui.nav_panel(
        "Compare Statistics",
        ui.row(
            ui.layout_columns(
                ui.card(
                    ui.input_selectize(
                        id="select_league",
                        label="select league",
                        choices=[1,2]
                    ),
                    ui.input_selectize(
                        id="select_team",
                        label="select team",
                        choices=[1,2]
                    ),
                    ui.input_checkbox_group(
                        id="select_season",
                        label="seaosn",
                        choices=["A","B","C"]
                    ),
                ),
                ui.card(
                    ui.h2("League", align="center"),
                    ui.card(
                        ui.row(
                            ui.layout_columns(
                                #TODO Make interactive through the server
                                ui.img(
                                    src="https://images.fotmob.com/image_resources/logo/teamlogo/9864_small.png",
                                    height="85%",
                                    width="85%",
                                    ),
                                ui.h2("Team"),
                                col_widths=(2,10), #image vs title
                            ),
                        ),
                        ui.row(
                            bokeh_dependency(),
                            ui.output_ui("figure", fill=True, fillable=True),
                            ui.output_text("text"),
                            align="center"
                        ),   
                        ui.row(
                            ui.layout_columns(
                                ui.card(
                                    ui.input_selectize(
                                    id="stat1",
                                    label="choose stat",
                                    choices=[1,2,3,4]
                                    ),
                                ),
                                ui.card(
                                    ui.input_selectize(
                                    id="stat2",
                                    label="choose stat 2",
                                    choices=[4,5,6,7]
                                    ),
                                ),
                                col_widths=(6,6), #selectize stats
                            ),
                        ),
                    ),    
                ),
                col_widths=(3,9), #sidebar vs panel
            ),
        ),
        ui.row(
            ui.card(
                ui.h2("Season Summary"),
                ui.layout_columns(
                    #TODO: Use classes for the background colors
                    ui.card(
                        ui.card_header("Points", class_="bg-primary-subtle"),
                        "Body",
                    ),
                    ui.card(
                        ui.card_header("Points", class_="bg-danger"),
                        "Body",
                    ),
                    ui.card(
                        ui.card_header("Points", class_="bg-success"),
                        "Body",
                    ),
                    ui.card(
                        ui.card_header("Points", class_="bg-info"),
                        "Body",
                    ),
                ),
                align="center",
            ),
        ),
        
    )

@module.server
def compare_stats_server(
    input: Inputs, output: Outputs, session: Session
):

    @output
    @render.text
    def text():
        return "Missing Graph"

    @output(id="figure")
    @render.ui
    def _():
        return ui.card(
            output_widget("bokeh"),
            full_screen=True,
        )

    @output(id="bokeh")
    @render_widget
    def _():
        x = [1, 2, 3, 4, 5]
        y = [6, 7, 2, 4, 5]
        p = figure(title="Simple line example", x_axis_label="x", y_axis_label="y")
        p.circle(x, y, legend_label="Temp.", line_width=2)
        return p
    
    @render.image
    def logo():
        return ImgData({"src": "stat-explorer/logo/4116_small.png", "width":"50px","height":"50px"})