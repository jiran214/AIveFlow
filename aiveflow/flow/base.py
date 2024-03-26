#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import Optional

from aiveflow.components import run_with_callbacks

from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from pydantic import BaseModel, PrivateAttr, Field


class Flow(BaseModel, abc.ABC):
    max_cost: Optional[int] = None
    max_token: Optional[int] = None
    max_rpm: Optional[int] = Field(None, description="Maximum number of requests per minute for the crew execution to be respected.")
    graph: StateGraph
    _compiled_graph: Optional[CompiledGraph] = PrivateAttr(None)

    @abc.abstractmethod
    def build(self, *args, **kwargs): ...

    def run(self, **initial_state):
        # build
        if not self._compiled_graph:
            self.build()
            self._compiled_graph = self.graph.compile()

        with run_with_callbacks(max_cost=self.max_cost, max_token=self.max_token, max_rpm=self.max_rpm):
            _output = self._compiled_graph.invoke(initial_state)
        return _output

    class Config:
        arbitrary_types_allowed = True
