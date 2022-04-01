#!/usr/bin/env python3

# Copyright 2019-2020 SURF.
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

from pathlib import Path

import typer
from fastapi.responses import JSONResponse
from structlog import get_logger

from orchestrator import OrchestratorCore
from orchestrator.cli.main import app as core_cli
from orchestrator.settings import AppSettings, app_settings
from settings import company_settings

from company import load_company, load_company_cli

logger = get_logger(__name__)


class OrchestratorResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"


def init_app(orchestrator_settings: AppSettings) -> OrchestratorCore:
    app = OrchestratorCore(base_settings=orchestrator_settings, default_response_class=OrchestratorResponse)
    load_company(app)
    return app


app_settings.TRANSLATIONS_DIR = Path(__file__).parent / "company" / "translations"
app_settings.WEBSOCKET_BROADCASTER_URL = f"redis://{app_settings.CACHE_HOST}:{app_settings.CACHE_PORT}"
app_settings.DISTLOCK_BACKEND = "redis"

logger.debug("Starting the app with the following settings", app_settings=str(app_settings))
app = init_app(app_settings)

if app_settings.TRACING_ENABLED:
    app.instrument_app()
    app.add_sentry(
        company_settings.SENTRY_DSN, company_settings.TRACE_SAMPLE_RATE, app_settings.SERVICE_NAME, app_settings.ENVIRONMENT
    )


def init_cli_app() -> typer.Typer:
    load_company_cli(core_cli)
    return core_cli()


if __name__ == "__main__":
    init_cli_app()
