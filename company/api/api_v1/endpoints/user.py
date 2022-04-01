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

"""Module that implements user (e.g. miscellaneous) related API endpoints."""

from http import HTTPStatus

import structlog
from fastapi.param_functions import Body
from fastapi.routing import APIRouter
from pydantic.types import Json

from orchestrator.api.models import create_or_update

from company.db import UserPreferenceTable
from company.schemas import UserPreferenceSchema

logger = structlog.get_logger(__name__)


router = APIRouter()


@router.get("/{domain}/{user_name}", response_model=UserPreferenceSchema)
def get_preferences(domain: str, user_name: str) -> dict:
    if query_result := UserPreferenceTable.query.get((domain, user_name)):
        return {"user_name": query_result.user_name, "domain": domain, "preferences": query_result.preferences}
    return {"user_name": user_name, "domain": domain, "preferences": {}}


@router.put("/{domain}/{user_name}", status_code=HTTPStatus.NO_CONTENT)
def update_preferences(domain: str, user_name: str, request_data: Json = Body(...)) -> None:
    user_pref = UserPreferenceSchema(
        **{"user_name": user_name, "domain": domain, "preferences": request_data.get("preferences")}  # type: ignore
    )
    create_or_update(UserPreferenceTable, user_pref)
