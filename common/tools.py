def config_to_str(config):
    s = "{"
    for section in config:
        s += f"{section}: {{"
        for key in config[section]:
            s += f"{key}: {config[section][key]}, "
        s = s[:-2]
        s += "}, "

    return s[:-2]
