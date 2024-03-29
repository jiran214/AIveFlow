#!/usr/bin/env python
# -*- coding: utf-8 -*-
import locale

import pycountry
from dotenv import load_dotenv

load_dotenv()


ROLE_CONTEXT_PROMPT = "Task result of {role}: {task_output}"
KNOWLEDGE_CONTEXT_PROMPT = "Answer the question based only on the following context:\n {knowledge_context}\n"
OPENAI_MODEL_NAME = 'gpt-3.5-turbo'
VECTOR_DB_DIR = 'db'

# task output language
LANGUAGE = 'auto'
