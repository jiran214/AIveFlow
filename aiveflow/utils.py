#!/usr/bin/env python
# -*- coding: utf-8 -*-
import locale
import threading
import time
import typing
from typing import Optional

import pycountry
from langchain_core.callbacks import BaseCallbackHandler
from pydantic import PrivateAttr, Field, BaseModel, model_validator
from rich.console import Console
from time import sleep

from rich.markdown import Markdown

from aiveflow import settings


def get_os_language():
    try:
        return pycountry.languages.get(alpha_2=locale.getdefaultlocale()[0].split('_')[0]).name
    except:
        return


class RPMController(BaseModel):
    max_rpm: int = Field(description="Maximum number of requests per minute for the crew execution to be respected.")
    _current_rpm: int = PrivateAttr(default=0)
    _timer: Optional[threading.Timer] = PrivateAttr(default=None)
    _lock: threading.Lock = PrivateAttr(default=None)

    def reset(self):
        self._lock = threading.Lock()
        self._reset_request_count()

    def exit(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def check_or_wait(self):
        with self._lock:
            if self._current_rpm < self.max_rpm:
                self._current_rpm += 1
            else:
                print("Max RPM reached, waiting for next minute to start.")
                self._wait_for_next_minute()
                self._current_rpm = 1

    def _wait_for_next_minute(self):
        time.sleep(60)
        self._current_rpm = 0

    def _reset_request_count(self):
        with self._lock:
            self._current_rpm = 0
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(60.0, self._reset_request_count)
        self._timer.start()


class Stop(Exception):
    pass


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

    def start(self, role_name, task_name=''):
        """配置初始化"""
        self.status = self.console.status(f"[bold green]{role_name} Working on {task_name[:10]}...")
        self.status.__enter__()

    def log(self, event, desc='', content=None):
        desc = desc or f": {desc}"
        self.console.print(f'[bold green]<{event}>{desc}')
        if content:
            self.print(content)

    def print(self, content):
        if '# ' in content:
            self.console.print(Markdown(f'{content}'))
        else:
            self.console.print(f'{content}')

    def end(self, output, last=False):
        event = 'Task Output'
        if last:
            event = 'Final Output'
        self.log(event, '', output)
        self.status.stop()


tracer = TaskTracer()