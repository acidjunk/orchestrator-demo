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

from typing import Callable
from uuid import UUID

from orchestrator.forms import FormPage
from orchestrator.forms.validators import DisplaySubscription, contact_person_list
from orchestrator.targets import Target
from orchestrator.types import InputForm, InputStepFunc, SubscriptionLifecycle, UUIDstr
from orchestrator.workflow import StepList, Workflow, done, init, make_workflow
from orchestrator.workflows.steps import resync, set_status, store_process_subscription, unsync
from orchestrator.workflows.utils import wrap_create_initial_input_form, wrap_modify_initial_input_form


def create_workflow(
    description: str,
    initial_input_form: InputStepFunc | None = None,
    status: SubscriptionLifecycle = SubscriptionLifecycle.ACTIVE,
) -> Callable[[Callable[[], StepList]], Workflow]:
    """Transform an initial_input_form and a step list into a workflow with a target=Target.CREATE.

    Use this for create workflows only.

    Example::

        @create_workflow("create service port")
        def create_service_port() -> StepList:
            do_something
            >> do_something_else
    """
    create_initial_input_form_generator = wrap_create_initial_input_form(initial_input_form)

    def _create_workflow(f: Callable[[], StepList]) -> Workflow:
        steplist = init >> f() >> set_status(status) >> resync >> done
        return make_workflow(f, description, create_initial_input_form_generator, Target.CREATE, steplist)

    return _create_workflow


def modify_workflow(
    description: str, initial_input_form: InputStepFunc | None = None
) -> Callable[[Callable[[], StepList]], Workflow]:
    """Transform an initial_input_form and a step list into a workflow.

    Use this for modify workflows.

    Example::

        @modify_workflow("create service port") -> StepList:
        def create_service_port():
            do_something
            >> do_something_else
    """

    wrapped_modify_initial_input_form_generator = wrap_modify_initial_input_form(initial_input_form)

    def _modify_workflow(f: Callable[[], StepList]) -> Workflow:
        steplist = (
            init
            >> store_process_subscription(Target.MODIFY)
            >> unsync
            >> f()
            >> resync
            >> done
        )

        return make_workflow(f, description, wrapped_modify_initial_input_form_generator, Target.MODIFY, steplist)

    return _modify_workflow


def terminate_initial_input_form_generator(subscription_id: UUIDstr, organisation: UUIDstr) -> InputForm:
    temp_subscription_id = subscription_id

    class TerminateForm(FormPage):
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore
        contact_persons: contact_person_list(UUID(organisation)) = []  # type: ignore

    return TerminateForm


def terminate_workflow(
    description: str, initial_input_form: InputStepFunc | None = None
) -> Callable[[Callable[[], StepList]], Workflow]:
    """Transform an initial_input_form and a step list into a workflow.

    Use this for terminate workflows.

    Example::

        @terminate_workflow("create service port") -> StepList:
        def create_service_port():
            do_something
            >> do_something_else
    """

    wrapped_terminate_initial_input_form_generator = wrap_modify_initial_input_form(initial_input_form)

    def _terminate_workflow(f: Callable[[], StepList]) -> Workflow:
        steplist = (
            init
            >> store_process_subscription(Target.TERMINATE)
            >> unsync
            >> f()
            >> set_status(SubscriptionLifecycle.TERMINATED)
            >> resync
            >> done
        )

        return make_workflow(f, description, wrapped_terminate_initial_input_form_generator, Target.TERMINATE, steplist)

    return _terminate_workflow
