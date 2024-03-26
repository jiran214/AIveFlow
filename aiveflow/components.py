#!/usr/bin/env python
# -*- coding: utf-8 -*-
from contextvars import ContextVar
from typing import Any, Optional

import threading
import time
from typing import Optional

from pydantic import PrivateAttr, Field, BaseModel
from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.tracers.context import register_configure_hook

from aiveflow.utils import RPMController


class RPMCallback(BaseCallbackHandler):
    _controller: Optional[RPMController] = None

    def __init__(self, max_rpm: Optional[int] = None):
        self._controller = RPMController(max_rpm=max_rpm)
        self._controller.reset()

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
            print(f'exceed cost: {self.total_cost}/{self.max_cost}')
        elif self.max_token and self.total_tokens > self.max_token:
            print(f'exceed token: {self.total_tokens}/{self.max_token}')
        else:
            self.should_continue = True


limit_callback_var: ContextVar[Optional[TokenLimitCallback]] = ContextVar(
    "limit_callback", default=None
)

rpm_callback_var: ContextVar[Optional[RPMCallback]] = ContextVar(
    "rpm_callback", default=None
)

register_configure_hook(limit_callback_var, True)
register_configure_hook(rpm_callback_var, True)