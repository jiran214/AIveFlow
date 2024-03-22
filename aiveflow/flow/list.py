#!/usr/bin/env python
# -*- coding: utf-8 -*-
import operator
from typing import List, TypedDict, Annotated, Sequence

from langgraph.graph import StateGraph, END
from pydantic import Field

from aiveflow import settings
from aiveflow.flow.base import Flow
from aiveflow.role.core import Role
from aiveflow.role.task import Task


class TaskState(TypedDict):
    role_name: str
    task_output: str
    # tools_used: List[str]


class ListFlowState(TypedDict):
    contexts: Annotated[List[TaskState], operator.add]


def get_context(state: ListFlowState, length):
    if state['contexts']:
        return '\n'.join(
            settings.CONTEXT_PROMPT.format(role=task['role_name'], task_output=task['task_output'])
            for task in state['contexts'][:length]
        )
    return ""


class ListFlow(Flow):
    steps: Sequence['Task']
    task_context_length: int = 2
    _graph: StateGraph = Field(default_factory=lambda: StateGraph(ListFlowState))

    @classmethod
    def auto(cls, goal: str, roles: Sequence[Role]):
        steps = ...
        return Flow(steps=steps)

    def task_wrapper(self, task: Task):
        assert task.chain

        def execute(state):
            _input = settings.TASK_INPUT_PROMPT.format(
                context=get_context(state, self.task_context_length),
                task_input=task.description
            )
            task._output = task.chain.invoke(_input)
            return {'contexts': [TaskState(role_name=task.role.name, task_output=task.output)]}

        return execute

    def build(self):
        node_keys = []
        for task in self.steps:
            task.prepare_execute()
            node_key = f"{task.role.name}:{task.description[:10]}..."
            self._graph.add_node(node_key, self.task_wrapper(task))
            if node_keys:
                self._graph.add_edge(node_keys[-1], node_key)
            node_keys.append(node_key)
        self._graph.add_edge(node_keys[-1], END)
        self._graph.set_entry_point(node_keys[0])

    def run(self):
        return super().run()['contexts'][-1]
