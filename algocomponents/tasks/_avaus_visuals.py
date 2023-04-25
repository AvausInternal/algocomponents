import os
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class AvausVisuals:
    """Helps create plots in Avaus colors and style

    All Avaus colors are hard coded into the class and uses by the plots it
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
    heatmap_palette = sns.light_palette(
        primary_colors["BLUEBERRY"], input="rgb", as_cmap=True
    )
    histogram_colors = [primary_colors["BLUEBERRY"], primary_colors["BLUEBERRY"]]
    histogram_palette = sns.set_palette(sns.color_palette(histogram_colors))

    def __init__(self):
        sns.set_style("whitegrid", {"axes.grid": False})

    def histplot(
        self,
        df: pd.DataFrame,
        x_col: str = None,
        y_cols: List[str] = None,
        title: str = None,
        legend: bool = False,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        sns.histplot(data=df, x=x_col, y=y_cols, palette=self.histogram_palette)
        self.visualize(
            title=title,
            legend=legend,
            show=show,
            file_name=file_name,
            output_folder=output_folder,
        )

    def heatmap(
        self,
        df: pd.DataFrame,
        title: str = None,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        sns.heatmap(data=df.corr(), cmap=self.heatmap_palette)
        self.visualize(
            title=title,
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
        legend: bool = False,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        if x_col and y_col:
            sns.boxplot(x=x_col, y=y_col, data=df, palette=self.primary_colors.values())
        else:
            sns.boxplot(data=df, palette=self.primary_colors.values())
        self.visualize(
            title=title,
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
        legend: bool = False,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        sns.countplot(x=x_col, data=df, hue=y_col, palette=self.primary_colors.values())
        self.visualize(
            title=title,
            legend=legend,
            show=show,
            file_name=file_name,
            output_folder=output_folder,
        )

    def visualize(
        self,
        title: str = None,
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
        plt.xlabel("")
        plt.ylabel("")
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
