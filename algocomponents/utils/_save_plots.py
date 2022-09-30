import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def save_boxplot(
        df: pd.DataFrame,
        output_folder: str = "",
        file_name: str = "boxplot"
):
    fig = plt.figure(figsize=(10, 7))
    sns.boxplot(data=df)

    if output_folder != "":
        output_folder = output_folder + "/"

    plt.savefig(f"{output_folder}{file_name}.png")
    print(f"Boxplot saved under \'{file_name}.png\' file")


def save_histogram(
        df: pd.DataFrame,
        output_folder: str = "",
        file_name: str = "histogram"
):
    fig = plt.figure(figsize=(10, 7))
    cols = df.columns
    for col in cols:
        sns.histplot(data=df, x=col)
        col_name = col.replace(" ", "_")
        plt.savefig(f"{output_folder}{file_name}-{col_name}.png")
        plt.clf()
        print(f"Histogram of a feature: \'{col}\' saved under \'{file_name}-{col_name}.png\' file")
