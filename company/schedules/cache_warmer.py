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


from orchestrator.schedules.scheduling import scheduler
from orchestrator.services.processes import start_process


@scheduler(name="Warm up cache", time_unit="minutes", period=30)
def run_cache_warmer() -> None:
    # Todo: implement an example task
    start_process("task_cache_warmer")
