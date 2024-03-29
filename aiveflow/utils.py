#!/usr/bin/env python
# -*- coding: utf-8 -*-
import locale
from enum import Enum
from typing import Union

import pycountry
from rich.console import Console
from rich.markdown import Markdown

from aiveflow import settings


def get_os_language():
    try:
        return pycountry.languages.get(alpha_2=locale.getdefaultlocale()[0].split('_')[0]).name
    except:
        return


class EventName(Enum):
    flow_start = 'Flow Start'
    task_start = 'Task Start'
    task_output = 'Task Output'
    tool_use = 'Tool Use'
    tool_output = 'Tool Output'
    warning = 'Warning'
    knowledge_learn = 'Learning knowledge'
    # final_output = 'Final Output'


class TaskTracer:
    """
    {Role} Working on Task "xxx" ...
    - <Tool Use>: ...
    - <Tool Output>: ...
    - <Task Output>: ...
    <End>: ...
    ...
    """
    console = Console()

    def __init__(self):
        self.status = None

    def log(self, event: Union[EventName, str], desc='', content=None):
        if event is EventName.tool_output and self.status:
            self.status.stop()
        elif event is EventName.task_start:
            self.status = self.console.status(desc)
            self.status.__enter__()
            return
        if isinstance(event, EventName):
            event = event.value
        desc = desc or f": {desc}"
        self.console.print(f'<{event}>{desc}')
        if content:
            self.print(content)

    def print(self, content):
        if '# ' in content:
            self.console.print(Markdown(f'{content}'))
        else:
            self.console.print(f'{content}')


class Stop(Exception):
    pass


def format_documents(docs):
    if not docs:
        return ''
    knowledge_context = '\n'.join(doc for doc in docs)
    knowledge_context = settings.KNOWLEDGE_CONTEXT_PROMPT.foramt(knowledge_context=knowledge_context)
    return knowledge_context


def RolePlay(role, backstory, goal):
    return f"You are {role}.\n{backstory}\n\nYour personal goal is: {goal}"


