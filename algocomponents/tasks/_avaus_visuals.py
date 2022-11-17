import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import List
import urllib.request
from urllib.request import urlopen


# TODO:
"""
-
violine plot
subplot
color palette 
sns.violinplot(data=df, x="deck", y="age", hue="alive", split=True)
"""


class AvausVisuals:
    """
    !Write doc-string here!!!
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
    scatterplot_color =  [
        primary_colors["BLUEBERRY"],
        secondary_colors["SKY"], 
        secondary_colors["CLOUDBERRY"],
        primary_colors["PINE"]
    ]
    barplot_color = sns.set_palette(sns.color_palette( ["#363760", "#135A61"]))
    heatmap_color = sns.light_palette("#363760", input="rgb", as_cmap=True)
    color = ["#135A61"]
    lineplot_color = sns.set_palette(sns.color_palette(color))
    Color2 =  ["#363760", "#135A61"]
    histo_color = sns.set_palette(sns.color_palette(Color2))

    def __init__(self):
        sns.set_style("whitegrid", {"axes.grid": False})

    def barplot(
        self,
        df: pd.DataFrame,
        title: str = None,
        file_name: str = None,
        output_folder: str = None,
        mono_color: bool = True,
        x_col: str = None,
        y_cols: List[str] = None,
        legend: bool = False,
    ):

        if x_col and y_cols:
            df_multi_transform = df_multi.melt(
                    x_col, var_name="Year", value_name="Sales"
                )
            if mono_color:
                
                sns.barplot(
                    data=df_multi_transform,
                    x=x_col,
                    y="Sales",
                    hue="Year",
                   color=self. color_list[0],
                   palette=self. color_list
                )
            else:

                sns.barplot(data=df, x=x_col, y=y_cols,  palette=self.color)
        else:
            if mono_color:
                sns.barplot(data=df, color=self. color_list[0])
            else:

                sns.barplot(data=df, palette=self.barplot_color)

        self.format(
            df=df, title=title, file_name=file_name, output_folder=output_folder, legend = legend 
        )

    def lineplot(
        self,
        df: pd.DataFrame,
        title: str = None,
        file_name: str = None,
        output_folder: str = None,
        x_col: str = None,
        y_cols: List[str] = None,
    ):

        sns.lineplot(
            data=df, x=x_col, y=y_cols, palette=self.lineplot_color, dashes=False
        )

        self.format(
            df=df, title=title, file_name=file_name, output_folder=output_folder
        )

    def histplot(
        self,
        df: pd.DataFrame,
        title: str = None,
        file_name: str = None,
        output_folder: str = None,
        x_col: str = None,
        y_cols: List[str] = None,
        legend: bool = False,
    ):
        sns.histplot(data=df, x=x_col, y=y_cols, palette =self.histo_color)
        self.format( 
            df=df, title=title, file_name=file_name, output_folder=output_folder, legend=legend
        )

    def heatmap(
        self,
        df: pd.DataFrame,
        title: str = None,
        file_name: str = None,
        x_col: str = None,
        y_cols: str = None,
        output_folder: str = None,
    ):
        sns.heatmap(data=df, cmap=self.heatmap_color)
        self.format(
            df=df, title=title, file_name=file_name, output_folder=output_folder
        )

    def scatterplot(
        self,
        df: pd.DataFrame,
        title: str = None,
        file_name: str = None,
        x_col: str = None,
        y_cols: str = None,
        output_folder: str = None,
        legend: bool = False,
        
       
    ):
        n_colors = len(df.columns)
        palette = self.scatterplot_color[:n_colors]
        sns.scatterplot(data=df,x=x_col, y=y_cols, palette= palette ,  s= 200)
        self.format(
            df=df, title=title, file_name=file_name, output_folder=output_folder, legend=legend ,  
        )

    def violinplot(
        self,
        df: pd.DataFrame,
        title: str = None,
        file_name: str = None,
        x_col: str = None,
        y_cols: str = None,
        hue: str = None,
        output_folder: str = None,
        legend: bool = False,
    ):
        sns.violinplot(
            data=df, x=x_col, y=y_cols, hue=hue, palette=self.color_list, split=True
        )
        self.format(
            df=df,
            title=title,
            file_name=file_name,
            output_folder=output_folder,
            legend=legend,
        )

    def pimp_my_plot(self):
        pass

    def format(
        self,
        df: pd.DataFrame,
        title: str = None,
        legend: bool = False,
        file_name: str = None,
        output_folder: str = None,
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

        # Save plot if path and name is defined
        if output_folder and file_name:
            print("save")

        # Show the plot
        plt.show()


if __name__ == "__main__":
    plotter = AvausVisuals()

    df_ab_test = pd.DataFrame([[0.10, 0.22]], columns=["Test", "Control"])

    df_monthly_sales = pd.DataFrame([[132, 232, 254, 343, 154, 222, 254, 343, 254, 323, 432, 267]], columns=["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"])
    df_sales_col = pd.DataFrame(
        [
            ["Jan", 12],
            ["Feb", 54],
            ["Mar", 34],
            ["Apr", 46],
            ["Maj", 96],
            ["Jun", 43],
            ["Jul", 43],
            ["Aug", 57],
            ["Sep", 43],
            ["Okt", 75],
            ["Nov", 32],
            ["Dec", 64],
        ],
        columns=["Month", "Sales"],
    )
    df_multi = pd.DataFrame(
        [
            ["Jan", 12, 23],
            ["Feb", 54, 23],
            ["Mar", 34, 23],
            ["Apr", 46, 23],
            ["Maj", 96, 23],
            ["Jun", 43, 23],
            ["Jul", 43, 23],
            ["Aug", 57, 23],
            ["Sep", 43, 23],
            ["Okt", 75, 23],
            ["Nov", 32, 23],
            ["Dec", 64, 23],
        ],
        columns=["Month", "Sales2021", "Sales2022"],
    )
    # df_multi = df_multi.any (axis = True )
    # df_multi_transform =  df_multi.melt ("Month", var_name= "Year", value_name= "Sales" )
    df_multi2 = pd.DataFrame(
        data={"Month": ["Jan", "Feb"], "Sales2021": [3, 4], "Sales2022": [5, 6]}
    )
    Index = ["aaa", "bbb", "ccc", "ddd", "eee"]
    Cols = ["A", "B", "C", "D"]
    df_heatmap = pd.DataFrame(abs(np.random.randn(5, 4)), index=Index, columns=Cols)
    df_scatter = pd.DataFrame(
        [[5.1, 3.5, 0,9], [4.9, 3.0, 0, 3], [7.0, 3.2, 1, 2], [6.4, 3.2, 1, 2], [5.9, 3.0, 2, 5]],
        columns=["length", "width", "species", "test"],
    )
  #print (df_scatter)
plotter.barplot (df= df_monthly_sales,title= "Barplot", )

plotter.scatterplot(df = df_scatter , title= "scatterplot", legend = True )
   
plotter.barplot(df=df_multi , title= "Barplot", x_col= "Month", y_cols =["Sales2021", "Sales2022"],  legend = True )
    #print (df_multi)
plotter.histplot (df = df_multi,title="Histplot")
plotter.violinplot(df=df_multi2, title="Violinplot")
plotter.heatmap(df=df_heatmap , title= "Heatmap")
plotter.lineplot(df=df_multi, title="Lineplot", x_col="Month", y_cols="Sales2021")


# Vi ska göra en klass som heter något smart, typ AvausPlotter eller något liknande
# Klassen ska sköta allt som har att göra med att läsa in fonts, definiera avaus-färger, osv
# Färger ska finnas tillgängliga som AvausPlotter.BLUEBERRY, AvausPlotter.PINE, etc. (eller kanske AvausPlotter.colors["BLUEBERRY"] ? Vad som blir bäst)
# Klassen kommer ha en metod per typ av plot, typ avaus_heatmap
# De kommer sen default:a till massa Avaus-färger, fonter osv, men det går att skicka in egna om man vill
# Metoderna kallar man typ så här:
# def heatmap(df: pd.DataFrame, output_folder: str = "", file_name: str = "histogram", interactive_plots: bool = True, logger: Logger = None, base_color = AvausPlotter.BLUEBERRY)
# (Utgår från det Karolina gjort här, som det här kommer att ersätta: https://github.com/AvausMI/algocomponents/pull/126/files)
# Vi kommer göra tasks för detta sen också, men börja med att göra det som en klass med metoder bara. Att de sen används i Tasks är en senare grej: det är det som Karolina börjat med men det kommer finnas massor av såna tasks sen


# font = ImageFont.truetype(Roboto)
"""""

def download(self, url):

     req = urllib.Request( url ) 
     content = urllib.urlopen( req )
     data = content.read()
     content.close()
     return data

url = 'https://fonts.google.com/download?family=Roboto'
dl = open(url)
data = dl.download(url)
""" ""
# print(font)


# pal = sns.color_palette(["#C5CDE4","#363760"])
# # specify the custom font to use
# sns.set_style({"font.family": "Roboto"})
# #plot Data

# data = [[30, 25, 50, 20],
# [40, 23, 51, 17],
# [35, 22, 45, 19]]
# X = np.arange(4)
# fig = plt.figure()
# ax = fig.add_axes([0,0,1,1])
# ax.bar(X + 0.00, data[0], color = "b", width = 0.25)
# ax.bar(X + 0.25, data[1], color = "g", width = 0.25)
# ax.bar(X + 0.50, data[2], color = "r", width = 0.25)
# plt.show()

# #Email.set_title ("email subscription ")
# plt.xlabel("")
# plt.ylabel("")
# plt.title (label="Email Subscription", fontsize = 20 , loc="left",  fontweight="bold" )
# #Email.set(xlabel="", ylabel="", title="some title")
# # # Remove all borders
# sns.despine(bottom = True, left = True)
# plt.show()
