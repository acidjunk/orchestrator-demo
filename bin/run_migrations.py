#!/usr/bin/env python3

from pathlib import Path

from alembic import command
from alembic.config import Config

from nwastdlib.logging import initialise_logging


def run_migrations() -> None:
    initialise_logging()

    path = Path(__file__).resolve().parent
    alembic_cfg = Config(file_=path / "../alembic.ini")
    command.upgrade(alembic_cfg, "heads")


if __name__ == "__main__":
    run_migrations()
