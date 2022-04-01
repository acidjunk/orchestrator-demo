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


from orchestrator.services.subscriptions import WF_BLOCKED_BY_IN_USE_BY_SUBSCRIPTIONS, WF_USABLE_MAP
from orchestrator.workflows import LazyWorkflowInstance

# Create
# LazyWorkflowInstance("company.workflows.core_link.create_core_link", "create_core_link")


# Modify
# LazyWorkflowInstance("company.workflows.core_link.modify_core_link_add_link", "modify_core_link_add_link")


# Task
# LazyWorkflowInstance("company.workflows.tasks.add_missing_ipv6_prefixes", "add_missing_ipv6_prefixes")


# Terminate
# LazyWorkflowInstance("company.workflows.core_link.terminate_core_link", "terminate_core_link")

# Validate
# LazyWorkflowInstance("company.workflows.core_link.validate_core_link", "validate_core_link")

WF_USABLE_MAP.update(
    {
    }
)

WF_BLOCKED_BY_IN_USE_BY_SUBSCRIPTIONS.update(
    {
    }
)
