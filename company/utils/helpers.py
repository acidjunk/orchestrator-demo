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
from itertools import groupby
from typing import Any, cast
from uuid import UUID

from structlog import get_logger

from orchestrator.forms.network_type_validators import BFD


logger = get_logger(__name__)


def array_to_comma_separated_string(list: list[str | int | bool | float]) -> str:
    """Return a comma with space separated string (", ") from a list with strings, integers, booleans and floats.

    Args:
        list: One list with strings, integers, booleans and floats.

    Returns: Comma with space separated string (", ").
    """
    return ", ".join(str(c) for c in list)


def create_bfd_summary_data(subscription: dict) -> list[str]:
    """Return summary data for bfd if the subscription has "bfd" dict.

    Args:
        subscription: A dict that might have "bfd" dict in it.

    Returns: Empty list or list with 3 strings.
    """
    data = []
    if "bfd" in subscription:
        bfd = cast(BFD, subscription["bfd"])
        data = [
            str(bfd.enabled),
            str(bfd.minimum_interval) if bfd.enabled else "N/A",
            str(bfd.multiplier) if bfd.enabled else "N/A",
        ]
    return data


def get_organisation_name(id: UUID) -> str:
    """Return organisation name by UUID.

    Args:
        id: UUID of Organisation.

    Returns: Organisation name as string.
    """

    # Todo: implement your own CRM client
    # return crm.get_organisation_by_uuid(id).name
    return "Company"
