# -*- coding: utf-8 -*-
from configparser import ConfigParser
import os

def get_config():
    """Helper function to get the config"""
    config = ConfigParser()
    config_file = "config-local.ini"
    if  os.path.exists(config_file):
        config.read(config_file)
    # Check if there are environment variables
    for k, v in os.environ.items():
        for section in ("investec", "sageone"):
            if not config.has_section(section):
                config.add_section(section)
            if k.startswith("%s_" % section.upper()):
                option = k.split("_", 1)[1].lower()
                config.set(section, option, v)
    return config