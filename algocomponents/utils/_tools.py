def config_to_str(config):
    config_dict = dict(config)
    for section in config:
        config_dict[section] = dict(config[section])

    return str(config_dict)


def merge_configs(merge_this, into_this, overwrite: bool = False):
    # Use .keys() instead of .sections() to also get the DEFAULT-section
    for section in merge_this.keys():
        if section not in into_this.keys():
            into_this.add_section(section)
        for key, value in merge_this[section].items():
            if key in into_this[section].keys() and not overwrite:
                continue
            into_this[section][key] = value

    return into_this
