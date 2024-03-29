#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
from typing import Optional

from langchain_core.runnables import Runnable

from aiveflow import settings, Task
from aiveflow.callbacks import run_with_callbacks

from langgraph.graph import StateGraph
from pydantic import PrivateAttr, Field

from aiveflow.role.core import Node


class Flow(Node, abc.ABC):
    log: bool = True
    max_cost: Optional[int] = None
    max_token: Optional[int] = None
    max_rpm: Optional[int] = Field(None, description="Maximum number of requests per minute for the crew execution to be respected.")
    graph: StateGraph
    chain: Optional[Runnable] = None

    def task_wrapper(self, task: Task):
        def execute(state):
            inputs = self.on_task_start(state, task)
            _output = task.chain.invoke(inputs)
            return self.on_task_end(_output, task)
        return execute

    @abc.abstractmethod
    def on_task_start(self, state: dict, task: Task) -> dict:
        """
        task start hook
        Args:
            state: Flow State
            task: Task object

        Returns:
            task input str
        """

    @abc.abstractmethod
    def on_task_end(self, task_output, task: Task) -> Optional[dict]:
        """
        task end hook
        Args:
            task_output: Task output
            task: Task object

        Returns:
            flow node output
        """

    @abc.abstractmethod
    def build(self, *args, **kwargs): ...

    def run(self, initial_state=None):
        # build
        if not self.chain:
            self.build()
            self.chain = self.graph.compile()
            self.chain = self.chain.with_config(tags=['flow'])

        with run_with_callbacks(max_cost=self.max_cost, max_token=self.max_token, max_rpm=self.max_rpm, log=self.log):
            _output = self.chain.invoke(initial_state or {})
        return _output

    def __str__(self):
        return f'flow:{self.id}'

    class Config:
        arbitrary_types_allowed = True
