import pandas as pd
import plotly.express as px
import plotly


def save_boxplot(df: pd.DataFrame, output_folder: str = "", file_name: str = "boxplot"):
    if output_folder == "" or output_folder[-1] == "/":
        pass
    else:
        output_folder = output_folder + "/"

    fig = px.box(df)
    fig.write_image(f"{output_folder}{file_name}.png")
    print(f"Boxplot saved under '{file_name}.png' file")
    plotly.offline.plot(fig, filename=f"{output_folder}{file_name}.html")
    print(f"Boxplot saved under '{file_name}.html' file")


def save_histogram(
    df: pd.DataFrame, output_folder: str = "", file_name: str = "histogram"
):
    if output_folder == "" or output_folder[-1] == "/":
        pass
    else:
        output_folder = output_folder + "/"

    cols = df.columns
    for col in cols:
        col_name = col.replace(" ", "_")
        fig = px.histogram(df, x=col)
        fig.write_image(f"{output_folder}{file_name}-{col_name}.png")
        print(
            f"Histogram of a feature: '{col}' saved under '{file_name}-{col_name}.png' file"
        )
        plotly.offline.plot(fig, filename=f"{output_folder}{file_name}-{col_name}.html")
        print(
            f"Histogram of a feature: '{col}' saved under '{file_name}-{col_name}.html' file"
        )
