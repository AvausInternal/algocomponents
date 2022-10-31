import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 


class AvausVisuals:

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

    # def __init__(self):

    def bar_chart(
        self,
        df: pd.DataFrame,
        output_folder: str = None,
        file_name: str = None,
        base_color: str = None,
    ):
        base_color = base_color or self.primary_colors["BLUEBERRY"]

        #create color palette
        # pal = sns.color_palette([self.primary_colors["BLUEBERRY"], self.primary_colors["BLUEBERRY"]])
        # specify the custom font to use
        # sns.set_style({'font.family': 'Roboto'})
        #plot Data 
        # sns.countplot(x=df.columns, data=df, palette=pal) 

        df.plot(kind="bar")
        plt.show()


        # df.plot.bar(x="City", y="Customers", rot=0)
        # #Email.set_title ('email subscription ')
        # plt.xlabel('')
        # plt.ylabel('')
        # # plt.title (label='Email Subscription', fontsize = 20 , loc="left",  fontweight="bold" )
        # #Email.set(xlabel='', ylabel='', title='some title')
        # # Remove all borders
        # sns.despine(bottom = True, left = True)
        # plt.show()



        if output_folder and file_name:
            print("save")

    def line_chart(self):
        pass

    def heatmap(
        self,
    ):
        pass


if __name__ == "__main__":
    plotter = AvausVisuals()
    # print(plotter.primary_colors["BLUEBERRY"])

    # df = pd.DataFrame({'City':['Stockholm', 'Göteborg', 'Malmö'], 'Customers':[10, 30, 20]})

    df = pd.DataFrame([[10, 22]], columns=["Stockolhm", "Gothenburg"])
    print(df.head())
    plotter.bar_chart(df=df)


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
