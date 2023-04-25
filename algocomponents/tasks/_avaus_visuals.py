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
    color_list = ["#363760", "#135A61", "#FAEFED", "#515458"]
    scatterplot_color = [
        primary_colors["BLUEBERRY"],
        secondary_colors["SKY"],
        secondary_colors["CLOUDBERRY"],
        primary_colors["PINE"],
    ]
    violin1 = [primary_colors["BLUEBERRY"]]
    barplot_color = sns.set_palette(sns.color_palette(["#363760", "#135A61"]))
    heatmap_color = sns.light_palette("#363760", input="rgb", as_cmap=True)
    color = ["#135A61"]
    lineplot_color = sns.set_palette(sns.color_palette(color))
    Color2 = ["#363760", "#135A61"]
    histo_color = sns.set_palette(sns.color_palette(Color2))

    def __init__(self):
        sns.set_style("whitegrid", {"axes.grid": False})

    def barplot(
        self,
        df: pd.DataFrame,
        mono_color: bool = True,
        x_col: str = None,
        y_cols: List[str] = None,
        title: str = None,
        legend: bool = False,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        if x_col and y_cols:
            df_multi_transform = df.melt(x_col, var_name="Year", value_name="Sales")
            if mono_color:
                sns.barplot(
                    data=df_multi_transform,
                    x=x_col,
                    y="Sales",
                    hue="Year",
                    color=self.color_list[0],
                    palette=self.color_list,
                )
            else:
                sns.barplot(data=df, x=x_col, y=y_cols, palette=self.color)
        else:
            if mono_color:
                sns.barplot(data=df, color=self.color_list[0])
            else:
                sns.barplot(data=df, palette=self.barplot_color)
        self.visualize(
            title=title,
            legend=legend,
            show=show,
            file_name=file_name,
            output_folder=output_folder
        )

    def lineplot(
        self,
        df: pd.DataFrame,
        x_col: str = None,
        y_cols: List[str] = None,
        title: str = None,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        sns.lineplot(
            data=df, x=x_col, y=y_cols, palette=self.lineplot_color, dashes=False
        )
        self.visualize(
            title=title,
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
        legend: bool = False,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        sns.histplot(data=df, x=x_col, y=y_cols, palette=self.histo_color)
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
        sns.heatmap(data=df.corr(), cmap=self.heatmap_color)
        self.visualize(
            title=title,
            show=show,
            file_name=file_name,
            output_folder=output_folder,
        )

    def scatterplot(
        self,
        df: pd.DataFrame,
        x_col: str = None,
        y_cols: str = None,
        title: str = None,
        legend: bool = False,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        n_colors = len(df.columns)
        palette = self.scatterplot_color[:n_colors]
        sns.scatterplot(data=df, x=x_col, y=y_cols, palette=palette, s=200)
        self.visualize(
            title=title,
            legend=legend,
            show=show,
            file_name=file_name,
            output_folder=output_folder,
        )

    def violinplot(
        self,
        df: pd.DataFrame,
        x_col: str = None,
        y_cols: str = None,
        hue: str = None,
        title: str = None,
        legend: bool = False,
        show: bool = True,
        file_name: str = None,
        output_folder: str = None,
    ):
        sns.violinplot(
            data=df, x=x_col, y=y_cols, hue=hue, palette=self.violin1, split=True
        )
        self.visualize(
            title=title,
            legend=legend,
            show=show,
            file_name=file_name,
            output_folder=output_folder,
        )

    # Use for continuous features
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

    # Use for categorical features
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

        # TODO Check if y-columns contain negative numbers
        # num = df.select_dtypes(include=np.number)
        # if (num["Sales2021"] > 0).any():
        # plt.ylim(bottom=0)

        if show:
            plt.show()
        if file_name and output_folder:
            if not os.path.isdir(output_folder):
                os.makedirs(output_folder)
            plt.savefig(os.path.join(output_folder, file_name))
        elif file_name:
            plt.savefig(file_name)

        plt.close()
