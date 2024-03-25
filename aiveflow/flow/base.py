#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import Optional

from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from pydantic import BaseModel, PrivateAttr


class Flow(BaseModel, abc.ABC):
    graph: StateGraph
    _compiled_graph: Optional[CompiledGraph] = PrivateAttr(None)

    @abc.abstractmethod
    def build(self, *args, **kwargs): ...

    def run(self, **initial_state):
        if not self._compiled_graph:
            self.build()
            self._compiled_graph = self.graph.compile()
        _output = self._compiled_graph.invoke(initial_state)
        return _output

    class Config:
        arbitrary_types_allowed = True