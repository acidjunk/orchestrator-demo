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


from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, Sequence, TypeVar
from urllib import parse
from uuid import UUID

import structlog
from pynso import DatastoreType
from structlog.threadlocal import tmp_bind

from orchestrator.types import State
from orchestrator.utils.errors import ApiException
from orchestrator.utils.json import json_dumps

from company.settings import external_service_settings
from company.utils.external import nso_api_client

logger = structlog.get_logger(__name__)


SERVICES_ROOT_PATH = "tailf-ncs:services"
DEVICES_ROOT_PATH = "tailf-ncs:devices"


T = TypeVar("T")


def only_if_nso_enabled(f: Callable[..., T]) -> Callable[..., T]:
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        if not external_service_settings.NSO_ENABLED:
            raise Exception("NSO disabled")
        return f(*args, **kwargs)

    return wrapper


@only_if_nso_enabled
def create(path: Sequence[str], payload: dict) -> bool:
    """
    Deploy a service to NSO.

    Args:
        payload: a dict containing the service parameters.

    Returns: True

    """
    logger.debug("NSO payload: %s", payload)
    return nso_api_client.create_data_value(data_path=path, data=json_dumps(payload))


@only_if_nso_enabled
def update(path: Sequence[str], payload: dict) -> bool:
    """
    Deploy a service to NSO.

    Args:
        path: the nso service path
        payload: a dict containing the updated service parameters.

    Returns: True

    """
    return nso_api_client.set_data_value(data_path=path, data=json_dumps(payload))


@only_if_nso_enabled
def get(path: Sequence[str], *, datastore: DatastoreType = None, params: dict[str, Any] | None = None) -> Any:
    return nso_api_client.get_data(data_path=path, datastore=datastore, params=params)


@only_if_nso_enabled
def delete(path: Sequence[str]) -> bool:
    """
    Remove the NSO service from the network.

    Args:
        path: the nso service path


    Returns: boolean

    """
    return nso_api_client.delete_path(data_path=path)


@only_if_nso_enabled
def call_operation(path: Sequence[str], data: dict | None = None) -> Any:
    if data is None:
        data = {}

    return nso_api_client.call_operation(data_path=path, data=data)


def create_node_path(node_name: str) -> list[str]:
    return [DEVICES_ROOT_PATH, f"device={node_name}"]


def create_service_path(service_type: str, service_id: str | UUID) -> list[str]:
    encoded_service_id = parse.quote_plus(str(service_id))
    return [SERVICES_ROOT_PATH, f'{service_type}="{encoded_service_id}"']


def get_all_services() -> dict:
    return get([SERVICES_ROOT_PATH], datastore=DatastoreType.CONFIG).get("tailf-ncs:services", {})


def get_service(service_type: str, service_id: str | UUID) -> State:
    return get(create_service_path(service_type, service_id), datastore=DatastoreType.CONFIG)


def get_node_info(node_name: str) -> dict:
    """
    Query NSO's devices based on node_name and return all the info.

    Args:
        node_name: the node name

    Returns: a dictionary with the NSO device info.

    """
    return get(
        create_node_path(node_name),
        params={
            "depth": 3,
            # If we get all it errors out on an invalid payload so we select the most interesting data here
            # The config field is actually one of the places where bogus is returned
            "fields": "name;address;port;description;authgroup;platform;state;device-type;service-list",
        },
    )


def set_node_unlocked(node_name: str) -> None:
    """
    Set NSO node to unlocked state.

    Args:
        node_name: the node name

    """
    update(create_node_path(node_name) + ["state", "admin-state"], {"admin-state": "unlocked"})


def is_in_sync(device_name: str) -> bool:
    """Check to see if a device is in sync according to NSO.

    Args:
        device_name: The device name to check the sync status of.

    Returns:
        True if in sync, False if not.

    Raises:
        Exception: if the underlying HTTP request returns anything other than HTTPStatus.OK.

    """
    with tmp_bind(logger, device_name=device_name) as log:
        resp = call_operation(create_node_path(device_name) + ["check-sync"])
        if resp["result"] == "error":
            log.error("Could not check sync status.", device=device_name, message=resp["info"])
            raise ApiException(status=HTTPStatus.BAD_REQUEST, reason=resp["info"])

        return resp["result"] == "in-sync"


def remove_empty_values(d: Any) -> Any:
    to_remove = [[], {}, "", ()]
    if type(d) is dict:
        return {
            k: remove_empty_values(v)
            for k, v in d.items()
            if v not in to_remove and remove_empty_values(v) not in to_remove
        }
    elif type(d) is list:
        return [remove_empty_values(v) for v in d if v not in to_remove and remove_empty_values(v) not in to_remove]
    else:
        return d
