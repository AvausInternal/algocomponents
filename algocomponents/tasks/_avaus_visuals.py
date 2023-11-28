import os
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FixedLocator, FixedFormatter


class AvausVisuals:
    """Creates plots in Avaus colors and style

    All Avaus colors are hard-coded into the class and are used by the plots it
    generates. Other stylized choices have also been made to make the plots look
    professional.

    """

    primary_colors = {
        "BLUEBERRY": "#363760",
        "ROSE": "#FAEFED",
        "STONE": "#515458",
        "PINE": "#135A61",
        "WHITE": "#FFFFFF",
    }
    secondary_colors = {
        "CLOUDBERRY": "#FF8709",
        "SKY": "#C5CDE4",
        "GRAVEL": "#EDEDEF",
        "WOOD": "#DEC8C0",
    }
    lineplot_color = sns.set_palette(sns.color_palette([primary_colors["PINE"]]))
    heatmap_palette = sns.light_palette(
        primary_colors["BLUEBERRY"], input="rgb", as_cmap=True
    )
    histogram_colors = [primary_colors["BLUEBERRY"], primary_colors["BLUEBERRY"]]
    histogram_palette = sns.set_palette(sns.color_palette(histogram_colors))

    def __init__(self):
        sns.set_style("whitegrid", {"axes.grid": False})

    def shorten_column_names(self, df, max_length=15):
        df_copy = df.copy()
        df_copy.columns = [
            col[:max_length] + "..." if len(col) > max_length else col
            for col in df.columns
        ]
        return df_copy

    def lineplot(
        self,
        df: pd.DataFrame,
        x_col: str = None,
        y_col: str = None,
        title: str = None,
        x_title: str = None,
        y_title: str = None,
        legend: bool = False,
        dashes: bool = False,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        sns.lineplot(
            data=df, x=x_col, y=y_col, palette=self.lineplot_color, dashes=dashes
        )
        self.visualize(
            title=title,
            x_col=x_col,
            y_col=y_col,
            x_title=x_title,
            y_title=y_title,
            legend=legend,
            show=show,
            file_name=file_name,
            output_folder=output_folder,
        )

    def histplot(
        self,
        df: pd.DataFrame,
        x_col: str = None,
        y_cols: List[str] = None,
        title: str = None,
        x_title: str = None,
        y_title: str = None,
        legend: bool = False,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        sns.histplot(data=df, y=y_cols, x=x_col, palette=self.histogram_palette)
        plt.subplots_adjust(left=0.25)

        # Get the current y-axis labels
        y_labels = [str(label.get_text()) for label in plt.gca().get_yticklabels()]

        # Truncate the labels
        truncated_labels = [
            label[:14] + "..." if len(label) > 15 else label for label in y_labels
        ]

        # Set the y-axis tick locations explicitly
        tick_locations = plt.gca().get_yticks()
        plt.gca().yaxis.set_major_locator(FixedLocator(tick_locations))

        # Set the y-axis labels with the truncated labels
        plt.gca().yaxis.set_major_formatter(FixedFormatter(truncated_labels))

        # Set the y-axis labels with the truncated labels
        plt.gca().set_yticklabels(truncated_labels)

        self.visualize(
            title=title,
            x_col=x_col,
            x_title=x_title,
            y_title=y_title,
            legend=legend,
            show=show,
            file_name=file_name,
            output_folder=output_folder,
        )

    def heatmap(
        self,
        df: pd.DataFrame,
        x_title: str = None,
        y_title: str = None,
        title: str = None,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        df_short_cols = self.shorten_column_names(df)
        sns.heatmap(data=df_short_cols.corr(), cmap=self.heatmap_palette)
        plt.subplots_adjust(left=0.23)
        plt.subplots_adjust(bottom=0.32)
        self.visualize(
            title=title,
            x_title=x_title,
            y_title=y_title,
            show=show,
            file_name=file_name,
            output_folder=output_folder,
        )

    def boxplot(
        self,
        df: pd.DataFrame,
        x_col: str = None,
        y_col: str = None,
        title: str = None,
        x_title: str = None,
        y_title: str = None,
        legend: bool = False,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        df_short_cols = self.shorten_column_names(df)
        if x_col and y_col:
            sns.boxplot(x=x_col, y=y_col, data=df, palette=self.primary_colors.values())
        else:
            sns.boxplot(
                data=df_short_cols, palette=self.primary_colors.values(), orient="h"
            )
        plt.subplots_adjust(left=0.25)
        self.visualize(
            title=title,
            x_col=x_col,
            y_col=y_col,
            x_title=x_title,
            y_title=y_title,
            legend=legend,
            show=show,
            file_name=file_name,
            output_folder=output_folder,
        )

    def countplot(
        self,
        df: pd.DataFrame,
        x_col: str = None,
        y_col: str = None,
        title: str = None,
        x_title: str = None,
        y_title: str = None,
        legend: bool = False,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        sns.countplot(x=x_col, data=df, hue=y_col, palette=self.primary_colors.values())
        self.visualize(
            title=title,
            x_col=x_col,
            y_col=y_col,
            x_title=x_title,
            y_title=y_title,
            legend=legend,
            show=show,
            file_name=file_name,
            output_folder=output_folder,
        )

    def scatterplot(
        self,
        df: pd.DataFrame,
        x_col: str = None,
        y_col: str = None,
        title: str = None,
        legend: bool = False,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None
    ):
        sns.scatterplot(data=df, x=x_col, y=y_col, color=self.primary_colors["PINE"])
        self.visualize(title=title, show=show, legend=legend, file_name=file_name, output_folder=output_folder)


    def visualize(
        self,
        title: str = None,
        x_col: str = None,
        y_col: str = None,
        x_title: str = None,
        y_title: str = None,
        legend: bool = False,
        show: bool = True,
        output_folder: str = None,
        file_name: str = None,
    ):
        # Add title if defined
        if title:
            plt.title(label=title, fontsize=20, loc="left", fontweight="bold")

        # Remove borders
        sns.despine(bottom=True, left=True)

        # Remove labels and add horizontal grid lines
        plt.xlabel(x_title if x_title else x_col)
        plt.ylabel(y_title if y_title else y_col)
        plt.grid(axis="y")

        # legend
        if legend:
            plt.legend(
                loc="upper center",
                bbox_to_anchor=(0.7, 1.10),
                fancybox=True,
                shadow=True,
                ncol=5,
            )

        if show:
            plt.show()
        if file_name and output_folder:
            if not os.path.isdir(output_folder):
                os.makedirs(output_folder)
            plt.savefig(os.path.join(output_folder, file_name))
        elif file_name:
            plt.savefig(file_name)

        plt.close()
