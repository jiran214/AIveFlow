#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from aiveflow.utils import get_os_language

CONTEXT_PROMPT = "{role}: {task_output}"
OPENAI_MODEL_NAME = 'gpt-3.5-turbo'

# task output language
LANGUAGE = get_os_language() or 'Chinese'