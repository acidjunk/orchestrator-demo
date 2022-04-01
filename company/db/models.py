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


import enum
from typing import Any

from sqlalchemy import (
    Column,
    Enum,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.dialects import postgresql as pg


from orchestrator.db.database import BaseModel


class UserPreferenceDomain(enum.Enum):
    DASHBOARD = 1


class UserPreferenceTable(BaseModel):
    """Used to store UserPreferences for e.g. the GUI configuration."""

    __tablename__ = "user_preference"
    user_name = Column(String(), nullable=False, index=True)
    domain = Column(Enum(UserPreferenceDomain))
    preferences = Column(pg.JSONB(), nullable=False)
    __table_args__: tuple[PrimaryKeyConstraint, dict[Any, Any]] = (PrimaryKeyConstraint("domain", "user_name"), {})
