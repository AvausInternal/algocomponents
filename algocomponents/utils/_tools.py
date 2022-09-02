def config_to_str(config):
    config_dict = dict(config)
    for section in config:
        config_dict[section] = dict(config[section])

    return str(config_dict)
