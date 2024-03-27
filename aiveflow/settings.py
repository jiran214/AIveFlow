#!/usr/bin/env python
# -*- coding: utf-8 -*-
import locale

import pycountry
from dotenv import load_dotenv

load_dotenv()


CONTEXT_PROMPT = "Task result of {role}: {task_output}"
OPENAI_MODEL_NAME = 'gpt-3.5-turbo'
log = True

# task output language
LANGUAGE = 'auto'