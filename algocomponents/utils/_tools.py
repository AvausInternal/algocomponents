from typing import Dict, List
import pandas as pd


def config_to_str(config) -> str:
    """Convert a ConfigParser-object to a string.

    This is used to log the contents of Tasks configs.

    Args:
        config: A ConfigParser object.

    Returns:
        A string representation of the ConfigParser.

    """
    config_dict = dict(config)
    for section in config:
        config_dict[section] = dict(config[section])

    return str(config_dict)


def merge_configs(merge_this, into_this, overwrite: bool = False):
    """Merge two ConfigParser-objects.

    When ConfigParser reads a second config, it always overwrites. This method
    is created in order to merge two configs without overwriting.

    Args:
        merge_this: The ConfigParser to put into another ConfigParser.
        into_this: The ConfigParser you wish to update.
        overwrite: Whether existing values in into_this should be kept or not.

    Examples:
        merge_this = {DEFAULT: {"a": 1, "b": 2,  "c": 3}}
        into_this  = {DEFAULT: {"a": 1, "b": 99, "d": 4}}
        overwrite  = False
        result     = {DEFAULT: {"a": 1, "b": 99, "c": 3, "d": 4}}

        merge_this = {DEFAULT: {"a": 1, "b": 2,  "c": 3}}
        into_this  = {DEFAULT: {"a": 1, "b": 99, "d": 4}}
        overwrite  = True
        result     = {DEFAULT: {"a": 1, "b": 2,  "c": 3, "d": 4}}

    Returns:
        The ConfigParser object which is the result of the merge.

    """
    # Assure DEFAULT is last, adding to this will add to all sections
    sections = merge_this.sections() + ["DEFAULT"]
    for section in sections:
        if section not in into_this.keys():
            into_this.add_section(section)
        for key, value in merge_this[section].items():
            if key in into_this[section].keys() and not overwrite:
                continue
            into_this[section][key] = value

    return into_this


def predict_with_model(
    model_path: str, metadata: Dict, df: pd.DataFrame, prediction_column: str = "score"
) -> pd.DataFrame:
    import os
    import joblib

    model_path = os.path.join(model_path, metadata["model_file"])
    model = joblib.load(filename=model_path)

    if "preprocessor_path" in metadata:
        pre_processor_path = os.path.join(model_path, metadata["preprocessor_path"])
        preprocessor = joblib.load(filename=pre_processor_path)
        df = preprocessor.transform(df)

    df[prediction_column] = model.predict(df)

    return df


def shuffle_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    new_df = df.copy()  # Create a copy of the original DataFrame
    for column in columns:
        shuffled_values = df[column].sample(frac=1).reset_index(drop=True)
        new_df[column] = shuffled_values
    return new_df
