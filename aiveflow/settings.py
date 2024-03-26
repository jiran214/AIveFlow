#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiveflow.utils import get_os_language
from dotenv import load_dotenv

load_dotenv()

CONTEXT_PROMPT = "{role}: {task_output}"
OPENAI_MODEL_NAME = 'gpt-3.5-turbo'

# task output language
LANGUAGE = get_os_language() or 'Chinese'