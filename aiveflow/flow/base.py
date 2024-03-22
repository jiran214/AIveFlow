#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc

from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from pydantic import BaseModel, PrivateAttr


class Flow(BaseModel, abc.ABC):
    graph: StateGraph
    _compiled_graph: CompiledGraph = PrivateAttr()

    @abc.abstractmethod
    def build(self, *args, **kwargs): ...

    def run(self):
        if not self._graph.compiled:
            self._graph.compile()
        _output = self._compiled_graph.invoke({})
        return _output

