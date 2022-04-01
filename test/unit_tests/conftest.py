# Copyright 2019-2022 SURF.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from contextlib import closing
from copy import deepcopy
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
import structlog
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker
from urllib3_mock import Responses

import orchestrator
from orchestrator import OrchestratorCore, app_settings
from orchestrator.db import ProductTable, SubscriptionCustomerDescriptionTable, db
from orchestrator.db.database import ENGINE_ARGUMENTS, SESSION_ARGUMENTS, BaseModel, Database, SearchQuery
from orchestrator.domain.base import SubscriptionModel
from orchestrator.forms import FormPage
from orchestrator.forms.network_type_validators import MTU
from orchestrator.services.subscriptions import RELATION_RESOURCE_TYPES
from orchestrator.services.translations import generate_translations
from orchestrator.types import SubscriptionLifecycle, UUIDstr
from orchestrator.utils.vlans import VlanRanges
from test.unit_tests.factories.ip_prefix import make_ip_prefix
from test.unit_tests.factories.service_port import make_service_port
from test.unit_tests.factories.sn7 import build_subscription_fixture, service_port_subscription_mapping
from test.unit_tests.factories.sn8 import make_static_ip_subscription
from test.unit_tests.workflows import WorkflowInstanceForTests
from test.unit_tests.workflows.shared.test_validate_subscriptions import validation_workflow

import company.schedules  # noqa: F401  Side-effects
from company import load_company
from company.config import PORT_SUBSCRIPTION_ID
from company.db import AvailabilityZoneTable, ClusterPortsTable
from company.db.models import DirectCloudZoneTable
from company.products.product_blocks.esi_l2vpn import Sn8L2VpnEsiBlockInactive
from company.products.product_blocks.fw_ip_gw_endpoint import FwIpGwEndpointBlockInactive
from company.products.product_blocks.fw_l2_endpoint import FwL2EndpointBlockInactive
from company.products.product_blocks.fw_l3_endpoint import FwL3EndpointBlockInactive
from company.products.product_blocks.ip_peer import PeerBlockInactive
from company.products.product_blocks.resource_type_types import (
    Asn,
    BgpExportPolicy,
    BgpHashAlgorithm,
    BgpSessionPriority,
    IpPeerPortType,
    PortMode,
    SurfCertFilter,
)
from company.products.product_blocks.sap_ip_sn8 import (
    Sn8IpBgpServiceAttachPointBlockInactive,
    Sn8IpStaticServiceAttachPointBlockInactive,
)
from company.products.product_blocks.sap_settings_l3vpn_sn8 import Sn8L3VpnServiceAttachPointSettingsBlockInactive
from company.products.product_blocks.sap_sn8 import Sn8ServiceAttachPointBlockInactive
from company.products.product_blocks.sn8_nsistp import NsistpBlockInactive
from company.products.product_types.dcc import DirectCloudConnectivityInactive
from company.products.product_types.firewall import FirewallInactive
from company.products.product_types.fw import FwInactive
from company.products.product_types.ip_peer import IpPeerInactive
from company.products.product_types.ip_peer_group import IpPeerGroup, IpPeerGroupInactive
from company.products.product_types.ip_peer_port import IpPeerPortInactive
from company.products.product_types.ip_prefix import IpPrefix
from company.products.product_types.node import Node, NodeInactive
from company.products.product_types.sn8_aggsp import Sn8AggregatedServicePortInactive
from company.products.product_types.sn8_corelink import Sn8CorelinkInactive
from company.products.product_types.sn8_ip import Sn8IpBgpInactive, Sn8IpStaticInactive
from company.products.product_types.sn8_irbsp import Sn8IrbServicePortInactive
from company.products.product_types.sn8_l2vpn import Sn8L2VpnInactive
from company.products.product_types.sn8_l3vpn import Sn8L3VpnInactive
from company.products.product_types.sn8_lp import Sn8LightPathInactive
from company.products.product_types.sn8_lr import Sn8LightPathRedundantInactive
from company.products.product_types.sn8_msc import Sn8MscInactive
from company.products.product_types.sn8_nsistp import NsistpInactive
from company.products.product_types.sp import Sn8ServicePortInactive
from company.products.product_types.surf_wireless import SurfWirelessInactive
from company.workflows.fwaas.shared_fw import short_uid
from company.workflows.node.create_node import SURFNET_NETWORK_UUID

logger = structlog.getLogger(__name__)


def run_migrations(db_uri: str) -> None:
    """
    Configure the alembic context and run the migrations.

    Each test will start with a clean database. This a heavy operation but ensures that our database is clean and
    tests run within their own context.

    Args:
        db_uri: The database uri configuration to run the migration on.

    Returns:
        None

    """
    path = Path(__file__).resolve().parent
    os.environ["DATABASE_URI"] = db_uri
    app_settings.DATABASE_URI = db_uri
    alembic_cfg = Config(file_=path / "../../alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_uri)

    version_locations = alembic_cfg.get_main_option("version_locations")
    alembic_cfg.set_main_option(
        "version_locations", f"{version_locations} {os.path.dirname(orchestrator.__file__)}/migrations/versions/schema"
    )

    command.upgrade(alembic_cfg, "heads")


@pytest.fixture(scope="session")
def db_uri(worker_id):
    """
    Ensure each pytest thread has its database.

    When running tests with the -j option make sure each test worker is isolated within its own database.

    Args:
        worker_id: the worker id

    Returns:
        Database uri to be used in the test thread

    """
    database_uri = os.environ.get("DATABASE_URI_TEST", "postgresql://orchestrator-demo:orchestrator-demo@localhost/orchestrator-demo-test")
    if worker_id == "master":
        # pytest is being run without any workers
        return database_uri
    url = make_url(database_uri)
    url = url.set(database=f"{url.database}-{worker_id}")
    return str(url)


@pytest.fixture(scope="session")
def database(db_uri):
    """Create database and run migrations and cleanup afterwards.

    Args:
        db_uri: fixture for providing the application context and an initialized database. Although specifying this
            as an explicit parameter is redundant due to `flask_app`'s autouse setting, we have made the dependency
            explicit here for the purpose of documentation.

    """
    db.update(Database(db_uri))
    url = make_url(db_uri)
    db_to_create = url.database
    url = url.set(database="postgres")

    engine = create_engine(url)
    with closing(engine.connect()) as conn:
        conn.execute("COMMIT;")
        conn.execute(f'DROP DATABASE IF EXISTS "{db_to_create}";')
        conn.execute("COMMIT;")
        conn.execute(f'CREATE DATABASE "{db_to_create}";')

    run_migrations(db_uri)
    db.wrapped_database.engine = create_engine(db_uri, **ENGINE_ARGUMENTS)

    try:
        yield
    finally:
        db.wrapped_database.engine.dispose()
        with closing(engine.connect()) as conn:
            conn.execute("COMMIT;")
            conn.execute(f'DROP DATABASE IF EXISTS "{db_to_create}";')


@pytest.fixture(autouse=True)
def db_session(database):
    """
    Ensure tests are run in a transaction with automatic rollback.

    This implementation creates a connection and transaction before yielding to the test function. Any transactions
    started and committed from within the test will be tied to this outer transaction. From the test function's
    perspective it looks like everything will indeed be committed; allowing for queries on the database to be
    performed to see if functions under test have persisted their changes to the database correctly. However once
    the test function returns this fixture will clean everything up by rolling back the outer transaction; leaving the
    database in a known state (=empty with the exception of what migrations have added as the initial state).

    Args:
        database: fixture for providing an initialized database.

    """
    with closing(db.wrapped_database.engine.connect()) as test_connection:
        db.wrapped_database.session_factory = sessionmaker(**SESSION_ARGUMENTS, bind=test_connection)
        db.wrapped_database.scoped_session = scoped_session(
            db.wrapped_database.session_factory, db.wrapped_database._scopefunc
        )
        BaseModel.set_query(cast(SearchQuery, db.wrapped_database.scoped_session.query_property()))

        trans = test_connection.begin()
        try:
            yield
        finally:
            trans.rollback()


@pytest.fixture(scope="session", autouse=True)
def fastapi_app(database, db_uri):
    RELATION_RESOURCE_TYPES.extend([PORT_SUBSCRIPTION_ID])
    app_settings.TRANSLATIONS_DIR = Path(__file__).parent.parent.parent / "company" / "translations"
    app_settings.DATABASE_URI = db_uri
    app = OrchestratorCore(base_settings=app_settings)
    load_company(app)
    return app


@pytest.fixture(scope="session", autouse=True)
def test_form_translations(worker_id):
    """Some voodoo to check for each form during test if the translations are complete."""

    translations = generate_translations("en-GB")["forms"]["fields"]
    used_translations = set()

    # In order to properly wrap a classmethod we need to do special stuff
    old_init_subclass = FormPage.__dict__["__init_subclass__"]

    # Wrapp a form function that is certain to be called to extract the used form fields
    @classmethod
    def init_subclass_wrapper(cls, *args, **kwargs: Any) -> None:
        # Skip forms in test modules
        if "test" not in cls.__module__:
            for field_name in cls.__fields__:
                used_translations.add(field_name)
                if (
                    field_name not in translations
                    and f"{field_name}_accept" not in translations
                    and not field_name.startswith("label_")
                ):
                    pytest.fail(f"Missing translation for field {field_name} in  {cls.__name__}")

        # Because the original is a classmethod we need to conform to the descriptor protocol
        return old_init_subclass.__get__(None, cls)(*args, **kwargs)

    FormPage.__init_subclass__ = init_subclass_wrapper
    try:
        yield
    finally:
        # unwrapp and check if all translations are actually used
        FormPage.__init_subclass__ = old_init_subclass

        # This check only works when you run without python-xdist because we need one single session
        # TODO this does not work reliable yet
        # if worker_id == "master":
        #     unused_keys = set()
        #     for trans_key in translations:
        #         if (
        #             not trans_key.endswith("_info")
        #             and not trans_key.endswith("_accept")
        #             and not trans_key.endswith("_fields")
        #             and trans_key not in used_translations
        #             and f"{trans_key}_accept" not in used_translations
        #         ):
        #             unused_keys.add(trans_key)

        #     if unused_keys:
        #         pytest.fail(f"found unused translations: {sorted(unused_keys)}", pytrace=False)


@pytest.fixture(autouse=True)
def responses():
    responses_mock = Responses("requests.packages.urllib3")

    def _find_request(call):
        mock_url = responses_mock._find_match(call.request)
        if not mock_url:
            pytest.fail(f"Call not mocked: {call.request}")
        return mock_url

    def _to_tuple(url_mock):
        return (url_mock["url"], url_mock["method"], url_mock["match_querystring"])

    with responses_mock:
        yield responses_mock

        mocked_urls = map(_to_tuple, responses_mock._urls)
        used_urls = map(_to_tuple, map(_find_request, responses_mock.calls))
        not_used = set(mocked_urls) - set(used_urls)
        if not_used:
            pytest.fail(f"Found unused responses mocks: {not_used}", pytrace=False)
