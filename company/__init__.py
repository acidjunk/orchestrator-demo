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

import aiocache
from typer import Typer

from orchestrator import OrchestratorCore
from orchestrator.settings import app_settings

# This has to happen on "import" time since the cache decorators also run on import time
aiocache.caches.add(
    "crm",
    {
        "cache": aiocache.RedisCache,
        "serializer": {"class": aiocache.serializers.JsonSerializer},
        "endpoint": app_settings.CACHE_HOST,
        "port": app_settings.CACHE_PORT,
        "ttl": 1800,
        "namespace": "orchestrator:crm",
    },
)


def load_company(app: OrchestratorCore) -> None:
    # Todo: add some products
    # import company.products  # noqa: F401  Side-effects
    import company.schedules  # noqa: F401  Side-effects
    # Todo: add some workflows
    # import company.workflows  # noqa: F401  Side-effects
    from company.api.api_v1.api import api_router

    app.include_router(api_router, prefix="/api")


def load_company_cli(app: Typer) -> None:
    pass
    # import company.products  # noqa: F401  Side-effects
    # import company.schedules  # noqa: F401  Side-effects
    # import company.workflows  # noqa: F401  Side-effects

    # Todo: implement a CLI command
    # app.add_typer(company.app, name="company")
