import pandas as pd
import plotly.express as px
import plotly
import os.path
from logging import Logger

from algocomponents.utils import LoggieDoggie


def save_boxplot(
    df: pd.DataFrame,
    output_folder: str = "",
    file_name: str = "boxplot",
    interactive_plots: bool = True,
    logger: Logger = None,
):
    save_file_path = os.path.join(output_folder, file_name)
    logger = logger or LoggieDoggie().fetch_logger(logger_name="save_boxplot")

    fig = px.box(df)
    fig.write_image(f"{save_file_path}.png")

    logger.info(f"Boxplot saved under '{save_file_path}.png' file")

    if interactive_plots:
        plotly.offline.plot(fig, filename=f"{save_file_path}.html")
        logger.info(f"Interactive boxplot saved under '{save_file_path}.html' file.")


def save_histogram(
    df: pd.DataFrame,
    output_folder: str = "",
    file_name: str = "histogram",
    interactive_plots: bool = True,
    logger: Logger = None,
):
    save_file_path = os.path.join(output_folder, file_name)
    logger = logger or LoggieDoggie().fetch_logger(logger_name="save_histogram")

    cols = df.columns
    for col in cols:
        col_name = col.replace(" ", "_")
        fig = px.histogram(df, x=col)
        fig.write_image(f"{save_file_path}-{col_name}.png")
        logger.info(
            f"Histogram of a feature: '{col}' saved under '{file_name}-{col_name}.png' file."
        )
        if interactive_plots:
            plotly.offline.plot(fig, filename=f"{save_file_path}-{col_name}.html")
            logger.info(
                f"Interactive histogram of a feature: '{col}' saved under '{file_name}-{col_name}.html' file."
            )


def save_corr_matrix(
    df: pd.DataFrame,
    output_folder: str = "",
    file_name: str = "corr_matrix",
    interactive_plots: bool = True,
    logger: Logger = None,
):
    save_file_path = os.path.join(output_folder, file_name)
    logger = logger or LoggieDoggie().fetch_logger(logger_name="save_corr_matrix")

    fig = px.imshow(df.corr())
    fig.write_image(f"{save_file_path}.png")
    logger.info(f"Correlation matrix saved under '{file_name}.png' file.")

    if interactive_plots:
        plotly.offline.plot(fig, filename=f"{save_file_path}.html")
        logger.info(
            f"Interactive correlation matrix saved under '{file_name}.html' file."
        )
