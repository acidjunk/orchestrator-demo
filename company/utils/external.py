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

"""Provides utility functions to (more) conveniently talk to external systems."""
import contextlib
from http import HTTPStatus
from typing import Any, Generator, Union
from uuid import UUID

import requests
import structlog
from opentelemetry import context  # type: ignore
from opentelemetry.instrumentation.utils import http_status_to_status_code
from opentelemetry.instrumentation.version import __version__
from opentelemetry.propagate import inject  # type: ignore
from opentelemetry.trace import Span, SpanKind, get_tracer  # type: ignore
from opentelemetry.trace.status import Status
from pynso import NSOClient

import crm_client
import ims_client
import ipam_client
import jira_client
from nwastdlib.url import URL
from orchestrator.api.error_handling import raise_status
from orchestrator.settings import app_settings, oauth2_settings
from orchestrator.types import UUIDstr
from orchestrator.utils.errors import is_api_exception

from company.settings import external_service_settings

logger = structlog.get_logger(__name__)

_SUPPRESS_HTTP_INSTRUMENTATION_KEY = "suppress_http_instrumentation"


def subscription_link(subscription_id: UUID | UUIDstr) -> str:
    workflows_gui = URL(app_settings.WORKFLOWS_GUI_URI)
    return str(workflows_gui / "subscription" / subscription_id)


@contextlib.contextmanager
def _suppress_further_instrumentation() -> Generator:
    token = context.attach(context.set_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY, True))
    try:
        yield
    finally:
        context.detach(token)


def _is_instrumentation_suppressed() -> bool:
    return bool(context.get_value("suppress_instrumentation") or context.get_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY))


class AuthMixin:
    """Authorization mixin for swagger-codegen generated ApiClients.

    This mixin ensures the proper OAuth2 header is set for API calls if OAuth2 has been enabled. It will also try
    to refresh the token and retry the call if it expects the token to be expired.

    IMPORTANT: AuthMixin should be the first class in the inheritance list!

    Given a Fubar API. Usage is::

        import fubar_client

        class FubarApiClient(AuthMixin, fubar_client.ApiClient)
            pass

    Calls to the Fubar API can now be make as follows::

        from fubar_client import BlahApi

        fac = FubarApiClient('https://api.staging.automation.surf.net/fubar')
        foo = BlaApi(fac).get_foo_by_id(foo_id)

    """

    configuration: crm_client.Configuration

    @staticmethod
    def _apply_response(span: Span, response: Any) -> None:
        if not span.is_recording():
            return

        if is_api_exception(response) and response.status:
            span.set_attribute("http.status_code", response.status)
            span.set_attribute("http.status_text", response.reason)
            span.set_status(Status(http_status_to_status_code(response.status)))
        else:
            span.set_attribute("http.status_code", 200)
            span.set_attribute("http.status_text", "OK")
            span.set_status(Status(http_status_to_status_code(200)))

    def acquire_token(self) -> None:
        if not hasattr(self.configuration, "access_token"):
            self.configuration.access_token = None

        if self.configuration.access_token:
            return
        else:
            if oauth2_settings.OAUTH2_ACTIVE:
                logger.debug("OAuth2 enabled. Requesting access token.", client=self.__class__.__name__)
                self.get_client_creds_token()

    def get_client_creds_token(self, force: bool = False) -> None:
        """Conditionally fetch access_token.

        Args:
            app: Application object that has a config attribute.
            force: Force the fetch, even if the access_token is already in the application configuration.

        """
        if not force and self.configuration.access_token:
            return

        response = requests.post(
            url=oauth2_settings.OAUTH2_TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(oauth2_settings.OAUTH2_RESOURCE_SERVER_ID, oauth2_settings.OAUTH2_RESOURCE_SERVER_SECRET),
            timeout=5,
        )
        if not response.ok:
            description = f"Response for obtaining access_token {response.json()}"
            raise_status(HTTPStatus.UNAUTHORIZED, detail=description)

        json = response.json()
        # Spec dictates that client credentials should not be allowed to get a refresh token
        self.configuration.access_token = json["access_token"]

    def call_api(  # type:ignore
        self, resource_path, method, path_params=None, query_params=None, header_params=None, *args, **kwargs
    ):
        span_attributes = {
            "http.method": method,
            "http.url": resource_path,
        }

        header_params = header_params if header_params is not None else {}
        # Check credentials
        self.acquire_token()

        with get_tracer(__name__, __version__).start_as_current_span(
            f"External Api Call {self.__class__.__name__}", kind=SpanKind.CLIENT, attributes=span_attributes
        ) as span:
            if app_settings.TRACING_ENABLED and not _is_instrumentation_suppressed():
                inject(type(header_params).__setitem__, header_params)
            try:
                with _suppress_further_instrumentation():
                    response = super().call_api(
                        resource_path, method, path_params, query_params, header_params, *args, **kwargs
                    )
                self._apply_response(span, response)
                return response
            except Exception as ex:
                if is_api_exception(ex) and ex.status in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                    logger.warning("Access Denied. Token expired? Retrying.", api_exception=str(ex))
                    self.get_client_creds_token(force=True)
                    with _suppress_further_instrumentation():
                        response = super().call_api(
                            resource_path, method, path_params, query_params, header_params, *args, **kwargs
                        )
                    self._apply_response(span, response)
                    return response
                else:
                    self._apply_response(span, ex)
                    logger.exception("Could not call API.", client=self.__class__.__name__)
                    raise


nso_api_client = NSOClient(
    external_service_settings.NSO_HOST,
    username=external_service_settings.NSO_USER,
    password=external_service_settings.NSO_PASS,
    port=external_service_settings.NSO_PORT,
    ssl=True,
    verify_ssl=external_service_settings.NSO_SSL_VERIFY,
)

