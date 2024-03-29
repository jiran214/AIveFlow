#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import time
import typing
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Union, Dict, List
from typing import Optional
from uuid import UUID

from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.tracers.context import register_configure_hook
from pydantic import BaseModel, Field, PrivateAttr

from aiveflow.utils import EventName, TaskTracer

if typing.TYPE_CHECKING:
    from aiveflow import Task


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
                tracer.log('<Tip>', "Max RPM reached, waiting for next minute to start.")
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


class RPMCallback(BaseCallbackHandler):
    _controller: Optional[RPMController] = None

    def __init__(self, max_rpm: Optional[int] = None):
        self._controller = RPMController(max_rpm=max_rpm)
        self._controller.reset()

    def on_chat_model_start(self, *args, **kwargs):
        self._controller.check_or_wait()

    def __del__(self):
        self._controller.exit()


class TokenLimitCallback(OpenAICallbackHandler):
    should_continue = True

    def __init__(self, max_cost: Optional[int] = None, max_token: Optional[int] = None):
        self.max_cost = max_cost
        self.max_token = max_token
        super().__init__()

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        super().on_llm_end(response, **kwargs)
        self.should_continue = False
        if self.max_cost and self.total_cost > self.max_cost:
            tracer.log(EventName.warning, f'exceed cost: {self.total_cost}/{self.max_cost}')
        elif self.max_token and self.total_tokens > self.max_token:
            tracer.log(EventName.warning, f'exceed token: {self.total_tokens}/{self.max_token}')
        else:
            self.should_continue = True


limit_callback_var: ContextVar[Optional[TokenLimitCallback]] = ContextVar(
    "limit_callback", default=None
)

rpm_callback_var: ContextVar[Optional[RPMCallback]] = ContextVar(
    "rpm_callback", default=None
)

trace_callback_var: ContextVar[Optional['TracerProxy']] = ContextVar(
    "trace_callback", default=None
)

task_context_var: ContextVar[Optional['Task']] = ContextVar(
    "task_context", default=None
)

register_configure_hook(limit_callback_var, True)
register_configure_hook(rpm_callback_var, True)
register_configure_hook(trace_callback_var, True)


@contextmanager
def run_with_callbacks(
    max_token=None, max_cost=None, max_rpm=None, log=False
):
    tracer.log(EventName.flow_start)
    rpm_callback = max_rpm and RPMCallback(max_rpm=max_rpm)
    limit_callback = (max_token or max_cost) and TokenLimitCallback(max_token=max_token, max_cost=max_cost)
    trace_callback = (log and tracer)
    limit_callback_var.set(limit_callback)
    rpm_callback_var.set(rpm_callback)
    trace_callback_var.set(trace_callback)
    yield
    # after run
    if rpm_callback:
        del rpm_callback
    limit_callback_var.set(None)
    rpm_callback_var.set(None)
    trace_callback_var.set(None)


class TracerProxy(BaseCallbackHandler):

    def __init__(self):
        self._tracer = TaskTracer()

    def log(self, event: Union[EventName, str], desc='', content=None):
        if trace_callback_var.get():
            self._tracer.log(event, desc, content)

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        self._tracer.log(EventName.tool_use, serialized['name'], serialized)

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        self._tracer.log(EventName.tool_output, '', output)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        self._tracer.log(EventName.task_output, '', response.generations[-1][-1].text)


tracer = TracerProxy()

