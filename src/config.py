"""
Central configuration for the Ethiopian GPS Navigation System.

This module centralizes core settings like data and output directories so they
can be reused consistently across the application and adjusted from a single
place. If needed, it can later be extended to read from environment variables
or configuration files.
"""

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration."""

    name: str = "Ethiopian GPS Navigation System"
    version: str = "1.0.0"

    # Resolve project root based on this file's location so paths
    # work regardless of the current working directory.
    project_root: Path = Path(__file__).resolve().parent.parent

    # Base directories (absolute paths under project root)
    data_dir: Path = project_root / "data"
    output_dir: Path = project_root / "output"

    # ------------------------------------------------------------------
    # Database configuration
    # ------------------------------------------------------------------
    # By default this project used a local SQLite database file.
    # To integrate with your MySQL database created in XAMPP
    # (named `ethiopian_gps`), we configure SQLAlchemy to use MySQL
    # via the `pymysql` driver. Adjust USER and PASSWORD as needed.
    #
    # Example for default XAMPP MySQL (user `root`, no password):
    #   mysql+pymysql://root@localhost/ethiopian_gps
    #
    # If you later set a password for root or another user, update
    # the URL accordingly, e.g.:
    #   mysql+pymysql://user:password@localhost/ethiopian_gps
    #
    # You can also override this at runtime using an environment
    # variable `GPS_DB_URL`. If it is set, that value will be used.
    _default_mysql_url: str = "mysql+pymysql://root@localhost/ethiopian_gps"
    database_url: str = os.getenv("GPS_DB_URL", _default_mysql_url)

    # Defaults for generated networks
    min_cities: int = 100
    min_roads: int = 500


def get_config() -> AppConfig:
    """
    Return the current application configuration instance.

    This indirection makes it easy to later load configuration from files or
    environment variables without changing import sites.
    """
    return AppConfig()

