def config_to_str(config):
    """Convert a ConfigParser-object to a string

    This is used to log the contents of Tasks configs

    """
    config_dict = dict(config)
    for section in config:
        config_dict[section] = dict(config[section])

    return str(config_dict)


def merge_configs(merge_this, into_this, overwrite: bool = False):
    """Merge two ConfigParser-objects

    When ConfigParser reads a second config, it always overwrites. This method
    is created in order to merge two configs without overwriting.

    Args:
        merge_this: The ConfigParser to put into another ConfigParser
        into_this: The ConfigParser you wish to update
        overwrite: Whether existing values in into_this should be kept or not

    Examples:
        merge_this = {DEFAULT: {"a": 1, "b": 2,  "c": 3}}
        into_this  = {DEFAULT: {"a": 1, "b": 99, "d": 4}}
        overwrite  = False
        result     = {DEFAULT: {"a": 1, "b": 99, "c": 3, "d": 4}}

        merge_this = {DEFAULT: {"a": 1, "b": 2,  "c": 3}}
        into_this  = {DEFAULT: {"a": 1, "b": 99, "d": 4}}
        overwrite  = True
        result     = {DEFAULT: {"a": 1, "b": 2,  "c": 3, "d": 4}}

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
