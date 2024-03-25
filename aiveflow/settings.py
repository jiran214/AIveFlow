#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from aiveflow.utils import get_os_language, RPMController

CONTEXT_PROMPT = "{role}: {task_output}"
OPENAI_MODEL_NAME = 'gpt-3.5-turbo'

# task output language
LANGUAGE = get_os_language() or 'Chinese'

_rpm_controller: Optional[RPMController] = None


# Maximum number of requests per minute for the crew execution to be respected.
def set_max_rpm(max_rpm: int):
    assert max_rpm > 0
    global _rpm_controller
    _rpm_controller = RPMController(max_rpm=max_rpm)
    _rpm_controller.reset()