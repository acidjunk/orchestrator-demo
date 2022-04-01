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
from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from company.products.services.subscription import subscription_description


def validate_subscription_description(subscription: SubscriptionModel) -> None:
    desired_description = subscription_description(subscription)
    if subscription.description != desired_description:
        raise AssertionError(
            f"Subscription description is invalid. Desired: {desired_description}, Actual: {subscription.description}"
        )


def validate_subscription_status_is_active(subscription: SubscriptionModel) -> None:
    if subscription.status != SubscriptionLifecycle.ACTIVE:
        raise AssertionError(f"Subscription status needs to be active but status is {subscription.status}")
