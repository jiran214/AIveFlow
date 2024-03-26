#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import Optional

from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from pydantic import BaseModel, PrivateAttr, Field

from aiveflow.components import limit_callback_var, TokenLimitCallback, RPMCallback, rpm_callback_var


class Flow(BaseModel, abc.ABC):
    max_cost: Optional[int] = None
    max_token: Optional[int] = None
    max_rpm: Optional[int] = Field(None, description="Maximum number of requests per minute for the crew execution to be respected.")
    graph: StateGraph
    _compiled_graph: Optional[CompiledGraph] = PrivateAttr(None)
    _limit_controller: Optional[TokenLimitCallback] = PrivateAttr(None)
    _rpm_controller: Optional[RPMCallback] = PrivateAttr(None)

    @abc.abstractmethod
    def build(self, *args, **kwargs): ...

    def run(self, **initial_state):
        # before run
        self._limit_controller = (self.max_token or self.max_cost) and TokenLimitCallback(max_token=self.max_token, max_cost=self.max_cost)
        self._rpm_controller = self.max_rpm and RPMCallback(max_rpm=self.max_rpm)
        # register global callback
        limit_callback_var.set(self._limit_controller)
        rpm_callback_var.set(self._rpm_controller)
        # build
        if not self._compiled_graph:
            self.build()
            self._compiled_graph = self.graph.compile()
        _output = self._compiled_graph.invoke(initial_state)
        # after run
        limit_callback_var.set(None)
        rpm_callback_var.set(None)
        del self._rpm_controller
        return _output

    class Config:
        arbitrary_types_allowed = True