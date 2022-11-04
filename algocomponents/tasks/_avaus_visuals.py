import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
from typing import List


#TODO: 
"""
-


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

    def __init__(self):
        sns.set_style("whitegrid", {'axes.grid' : False})
        
    def barplot(
        self,
        df: pd.DataFrame,
        title: str = None, 
        file_name: str = None,
        output_folder: str = None,
        mono_color: bool = True, 
        x_col: str = None, 
        y_cols: List[str] = None,
        # TODO: Pass "Year" and "Sales" in nice way and replace hardcoded
        #       "Sales" and "Year" below
    ):

        if x_col and y_cols:
            if mono_color:
                df_multi_transform = df_multi.melt(x_col, var_name="Year", value_name="Sales")
                sns.barplot(data=df_multi_transform, x=x_col, y="Sales", hue="Year", color=self.color_list[0])
            else: 
                sns.barplot(data=df, x=x_col, y=y_cols, palette=self.color_list)
        else: 
            if mono_color: 
                sns.barplot(data=df, color=self.color_list[0])
            else: 
                sns.barplot(data=df, palette=self.color_list)

        self.format(df=df, title=title, file_name=file_name, output_folder=output_folder)
       

    def lineplot(
        self,
        df: pd.DataFrame,
        title: str = None, 
        file_name: str = None,
        output_folder: str = None,
        x_col: str = None, 
        y_cols: List[str] = None,
    ):

        sns.lineplot(data=df, x=x_col, y=y_cols, palette=self.color_list, dashes=False)

        self.format(df=df, title=title, file_name=file_name, output_folder=output_folder)

    def heatmap(self):
        pass

    def pimp_my_plot(self):
        pass

    def format(self, 
        df: pd.DataFrame,
        title: str = None, 
        file_name: str = None,
        output_folder: str = None
        ):
            # Add title if defined 
            if title: 
                plt.title(label=title, fontsize=20, loc="left", fontweight="bold")
            
            # Remove borders 
            sns.despine(bottom = True, left = True)

            # Remove labels and add horizontal grid lines 
            plt.xlabel("")
            plt.ylabel("")
            plt.grid(axis="y")

            #TODO Check if y-columns contain negative numbers
            num = df.select_dtypes(include=np.number)
            if (num["Sales2021"] > 0).any(): 
                plt.ylim(bottom=0)

            # Save plot if path and name is defined
            if output_folder and file_name:
                print("save")

            # Show the plot
            plt.show()


if __name__ == "__main__":
    plotter = AvausVisuals()

    df_ab_test = pd.DataFrame([[0.10, 0.22]], columns=["Test", "Control"])

    # df_monthly_sales = pd.DataFrame([[132, 232, 254, 343, 154, 222, 254, 343, 254, 323, 432, 267]], columns=["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"])
    df_sales_col = pd.DataFrame([["Jan", 12],["Feb", 54],["Mar", 34], ["Apr", 46], ["Maj", 96], ["Jun", 43], ["Jul", 43], ["Aug", 57], ["Sep", 43], ["Okt", 75], ["Nov", 32], ["Dec", 64]], columns=["Month", "Sales"])

    df_multi = pd.DataFrame([["Jan", 12, 23],["Feb", 54, 23],["Mar", 34, 23], ["Apr", 46, 23], ["Maj", 96, 23], ["Jun", 43, 23], ["Jul", 43, 23], ["Aug", 57, 23], ["Sep", 43, 23], ["Okt", 75, 23], ["Nov", 32, 23], ["Dec", 64, 23]], columns=["Month", "Sales2021", "Sales2022"])

    plotter.barplot(df=df_multi, title="Sales", x_col="Month", y_cols=["Sales2021", "Sales2022"])


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
