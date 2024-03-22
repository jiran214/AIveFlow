#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiveflow.utils import get_os_language

CONTEXT_PROMPT = "{role}: {task_output}"
TASK_INPUT_PROMPT = "{context}\nYour task:\n{task_input}"
TASK_CONTEXT_LENGTH = 3
OPENAI_MODEL_NAME = 'gpt-3.5-turbo'
LANGUAGE = get_os_language() or 'Chinese'
