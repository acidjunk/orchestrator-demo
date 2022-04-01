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


import jinja2
from pydantic import BaseSettings


def template_environment(loader: jinja2.BaseLoader) -> jinja2.Environment:
    """
    Return a safe jinja2 environment to render a template.

    Args:
        loader: A loader.

    return:
        Jinja2 Environment

    """
    return jinja2.Environment(
        loader=loader, autoescape=True, lstrip_blocks=True, trim_blocks=True, undefined=jinja2.StrictUndefined
    )


class ExternalServiceSettings(BaseSettings):
    CRM_URI: str = "https://api.dev.automation.surf.net"
    JIRA_URI: str = "https://api.dev.automation.surf.net"
    JIRA_WUI_URI: str = "https://jira-test.surfnet.nl/browse"
    IMS_URI: str = "https://api.dev.automation.surf.net"
    IPAM_URI: str = "https://api.dev.automation.surf.net"
    SURFNET_NSA_URI: str = "http://surfnet8-nsa-stg:8091"
    NW_DASHBOARD_URL: str = "https://netwerkdashboard.dev.automation.surf.net"
    NSO_HOST: str = "nso-dev.vtb.automation.surf.net"
    NSO_USER: str = "ncsadmin"
    NSO_PASS: str = "ncsadmin"
    NSO_SSL_VERIFY: bool = True
    NSO_PORT: int = 8888
    NSO_ENABLED: bool = True
    DO_DNS_CHECKS: bool = True
    DO_NODE_IN_SYNC_CHECK: bool = True
    SET_NODE_UNLOCKED: bool = False
    NODE_IPV4_PREFIX: str = "10.1.4.0/22"
    NODE_IPV6_PREFIX: str = "fd00:0:100:1::/64"
    NODE_DNS_ZONE: str = "dev.vtb"
    CHECK_DNS_ZONE: str = "dev.vtb"
    CORELINK_IPV4_PREFIX: str = "10.1.16.0/20"
    CORELINK_IPV6_PREFIX: str = "fd00:0:101::/48"
    PTP_IPV4_PREFIX: str = "10.1.32.0/20"
    PTP_IPV6_PREFIX: str = "fd00:0:102::/48"
    IP_PEER_PORT_IPV4_ROOT_PREFIX: str = "145.145.166.0/23"
    IP_PEER_PORT_IPV6_ROOT_PREFIX: str = "2001:610:f16::/48"
    AUTONOMOUS_SYSTEM_NUMBER_ID: int = 1
    KLANT_VRF: int = 2
    INFRA_VRF: int = 1
    NOC_MAIL: str = "nwa-helpdesk-dev@list.surfnet.nl"
    EXTERNAL_SYSTEMS_TIMEZONE: str = "Europe/Amsterdam"
    WIKI_PRODUCT_LINK: str = "https://wiki.surfnet.nl/display/SURFnetnetwerkWiki/In+gebruik+nemen+nieuwe+service"


external_service_settings = ExternalServiceSettings()
