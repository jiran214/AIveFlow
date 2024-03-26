#!/usr/bin/env python
# -*- coding: utf-8 -*-
import operator
from typing import List, TypedDict, Annotated, Sequence, Union, Callable, Optional

from langchain_core.runnables import chain
from langgraph.graph import StateGraph, END
from pydantic import Field, model_validator

from aiveflow import settings
from aiveflow.flow.base import Flow
from aiveflow.role.core import Role
from aiveflow.role.task import Task


class TaskState(TypedDict):
    role_name: str
    task_output: str
    # tools_used: List[str]


class LineFlowState(TypedDict):
    contexts: Annotated[List[TaskState], operator.add]


def get_context(state: LineFlowState, length):
    if state['contexts']:
        return "This is the context you're working with:\n" + '\n'.join(
            settings.CONTEXT_PROMPT.format(role=task['role_name'], task_output=task['task_output'])
            for task in state['contexts'][-length:]
        ) + '\n'
    return ""


class LineFlow(Flow):
    steps: List['Task']
    task_context_length: int = 1
    graph: StateGraph = Field(default_factory=lambda: StateGraph(LineFlowState))

    @classmethod
    def auto(cls, goal: str, roles: Sequence[Role]):
        steps = []
        return Flow(steps=steps)

    def task_wrapper(self, task: Task):
        assert task.chain

        def execute(state):
            # inject
            if self._limit_controller and self._limit_controller.should_continue is False:
                return
            _input = dict(context=get_context(state, self.task_context_length))
            _output = task.chain.invoke(_input)
            role = getattr(task, 'role')
            role_name = (role and role.name) or task.chain.name
            return {'contexts': [TaskState(role_name=role_name, task_output=_output)]}

        return execute

    def build(self):
        node_keys = []
        for task in self.steps:
            self.graph.add_node(task.node_key, self.task_wrapper(task))
            if node_keys:
                self.graph.add_edge(node_keys[-1], task.node_key)
            node_keys.append(task.node_key)
        self.graph.add_edge(node_keys[-1], END)
        self.graph.set_entry_point(node_keys[0])

    def run(self, **initial_state):
        final_state = super().run(**initial_state)
        last_context = final_state['contexts'][-1]
        last_output = last_context['task_output']
        return last_output


if __name__ == '__main__':
    def task(state):
        _res = state['contexts'][-1]
        _res['task_output'] = str(int(_res['task_output']) + 1)
        state['contexts'] = [_res]
        return state

    flow = LineFlow(steps=[task, task])
    res = flow.run(contexts=[TaskState(role_name='test', task_output='0')])
    print(res)
    assert res == '2'