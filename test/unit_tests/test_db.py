import os
from operator import attrgetter

from alembic.config import Config
from alembic.script.base import ScriptDirectory
from more_itertools.more import groupby_transform

import orchestrator
from orchestrator import app_settings


def test_migration_heads(db_uri):
    """
    Check if there are only two migration heads.

    There should be one migration head for the surf specific stuff and one for the core specific stuff
    """
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    os.environ["DATABASE_URI"] = db_uri
    alembic_cfg = Config(file_=os.path.join(path, "../../alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", db_uri)
    version_locations = alembic_cfg.get_main_option("version_locations")
    alembic_cfg.set_main_option(
        "version_locations", f"{os.path.dirname(orchestrator.__file__)}/migrations/versions/schema {version_locations}"
    )
    script = ScriptDirectory.from_config(alembic_cfg)
    heads = script.get_revisions("heads")

    data = groupby_transform(heads, lambda i: i.branch_labels.pop(), attrgetter("revision"))

    for branch, heads in data:
        heads = list(heads)
        assert (
            len(heads) == 1
        ), f"Found more than two heads in {branch} run: DATABASE_URI={app_settings.DATABASE_URI} PYTHONPATH=. python main.py db merge {' '.join(heads)}"
