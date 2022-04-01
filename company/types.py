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
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from typing import Literal, TypedDict

from pydantic import EmailStr

Tags = Literal[
    "Node",
]


class MailAddress(TypedDict):
    email: EmailStr
    name: str


class ConfirmationMail(TypedDict):
    message: str
    subject: str
    language: str
    to: list[MailAddress]
    cc: list[MailAddress]
    bcc: list[MailAddress]


IPAddress = IPv4Address | IPv6Address
IPNetwork = IPv4Network | IPv6Network
