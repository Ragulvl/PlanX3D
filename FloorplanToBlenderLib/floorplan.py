"""
Floorplan
Data model representing a single floorplan configuration.
Loads settings from an INI config file and exposes them as attributes.
"""

import json
from typing import Optional

from . import const
from . import config


def new_floorplan(config_path: Optional[str] = None) -> "Floorplan":
    """
    Factory function — create a Floorplan from a config file path.

    @Param config_path: path to INI file, or None for default
    @Return: configured Floorplan instance
    """
    return Floorplan(config_path)


class Floorplan:
    """
    Represents a single floorplan with all settings loaded from an INI config.

    Attributes are dynamically set from the config sections (IMAGE, TRANSFORM,
    FEATURES, EXTRA_SETTINGS, WALL_CALIBRATION).
    """

    def __init__(self, conf: Optional[str] = None):
        if conf is None:
            conf = const.IMAGE_DEFAULT_CONFIG_FILE_NAME
        self.conf: str = conf
        self.create_variables_from_config(self.conf)

    def __str__(self) -> str:
        return str(vars(self))

    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items() if k != "conf")
        return f"Floorplan(conf={self.conf!r}, {attrs})"

    def create_variables_from_config(self, conf: str) -> None:
        """Parse INI file and set each key-value pair as an instance attribute."""
        settings = config.get_all(conf)
        settings_dict = {s: dict(settings.items(s)) for s in settings.sections()}
        for group in settings_dict.items():
            for item in group[1].items():
                setattr(self, item[0], json.loads(item[1]))
