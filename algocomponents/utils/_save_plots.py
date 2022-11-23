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
    open_interactive_plot: bool = True,
    logger: Logger = None,
):
    """Function that saves boxplot of columns in given dataset.

    It takes a dataset as pandas DataFrame
    and saves boxplot in specified folder in .png format.
    If argument 'interactive_plots' is set to True, it additionally
    saves plotly interactive plot with .html format.

    Args:
        df (pd.DataFrame): Pandas DataFrame with dataset to visualize.
        output_folder (str, optional): Folder name or folder path, where to save plot.
        file_name (str, optional): Name of destination file.
        interactive_plots (bool, optional): Whether to additionally save interactive plot.
        open_interactive_plot (bool, optional): Whether to open the plot on completion.
        logger (Logger, optional): Specific Logger if desired.

    """
    save_file_path = os.path.join(output_folder, file_name)
    logger = logger or LoggieDoggie().fetch_logger(logger_name="save_boxplot")

    fig = px.box(df)
    fig.write_image(f"{save_file_path}.png")

    logger.info(f"Boxplot saved under '{save_file_path}.png' file")

    if interactive_plots:
        plotly.offline.plot(
            fig, filename=f"{save_file_path}.html", auto_open=open_interactive_plot
        )
        logger.info(f"Interactive boxplot saved under '{save_file_path}.html' file.")


def save_histogram(
    df: pd.DataFrame,
    output_folder: str = "",
    file_name: str = "histogram",
    interactive_plots: bool = True,
    open_interactive_plot: bool = True,
    logger: Logger = None,
):
    """Function that saves histogram of each column in given dataset.

    It takes a dataset as pandas DataFrame
    and saves saves histograms in specified folder in .png format.
    If argument 'interactive_plots' is set to True, it additionally
    saves plotly interactive plots with .html format.

    Args:
        df (pd.DataFrame): Pandas DataFrame with dataset to visualize.
        output_folder (str, optional): Folder name or folder path, where to save plots.
        file_name (str, optional): Name of destination file, with column name suffix.
        interactive_plots (bool, optional): Whether to additionally save interactive plots.
        open_interactive_plot (bool, optional): Whether to open the plot on completion.
        logger (Logger, optional): Specific Logger if desired.

    """
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
            plotly.offline.plot(
                fig,
                filename=f"{save_file_path}-{col_name}.html",
                auto_open=open_interactive_plot,
            )
            logger.info(
                f"Interactive histogram of a feature: '{col}' saved under '{file_name}-{col_name}.html' file."
            )


def save_corr_matrix(
    df: pd.DataFrame,
    output_folder: str = "",
    file_name: str = "corr_matrix",
    interactive_plots: bool = True,
    open_interactive_plot: bool = True,
    logger: Logger = None,
):
    """Function that saves correlation matrix of columns in given dataset.

    It takes a dataset as pandas DataFrame
    and saves saves correlation matrix in specified folder in .png format.
    If argument 'interactive_plots' is set to True, it additionally
    saves plotly interactive plot with .html format.

    Args:
        df (pd.DataFrame): Pandas DataFrame with dataset to visualize.
        output_folder (str, optional): Folder name or folder path, where to save plot.
        file_name (str, optional): Name of destination file.
        interactive_plots (bool, optional): Whether to additionally save interactive plot.
        open_interactive_plot (bool, optional): Whether to open the plot on completion.
        logger (Logger, optional): Specific Logger if desired.

    """
    save_file_path = os.path.join(output_folder, file_name)
    logger = logger or LoggieDoggie().fetch_logger(logger_name="save_corr_matrix")

    fig = px.imshow(df.corr())
    fig.write_image(f"{save_file_path}.png")
    logger.info(f"Correlation matrix saved under '{file_name}.png' file.")

    if interactive_plots:
        plotly.offline.plot(
            fig, filename=f"{save_file_path}.html", auto_open=open_interactive_plot
        )
        logger.info(
            f"Interactive correlation matrix saved under '{file_name}.html' file."
        )
