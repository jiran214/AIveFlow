#!/usr/bin/env python
# -*- coding: utf-8 -*-
import operator
from typing import List, TypedDict, Annotated, Sequence, Union

from langgraph.graph import StateGraph, END
from pydantic import Field, model_validator

from aiveflow import settings
from aiveflow.callbacks import limit_callback_var, tracer
from aiveflow.flow.base import Flow
from aiveflow.role.core import Role, Node
from aiveflow.role.task import Task
from aiveflow.utils import EventName


class TaskState(TypedDict):
    role_name: str
    task_output: str
    # tools_used: List[str]


class SequentialFlowState(TypedDict):
    contexts: Annotated[List[TaskState], operator.add]


def get_context(state: SequentialFlowState, length):
    if state['contexts']:
        return "This is the context you're working with:\n" + '\n'.join(
            settings.CONTEXT_PROMPT.format(role=task['role_name'], task_output=task['task_output'])
            for task in state['contexts'][-length:]
        ) + '\n'
    return ""


class SequentialFlow(Flow):
    steps: List[Union['Task', 'Flow']]
    task_context_length: int = 1
    graph: StateGraph = Field(default_factory=lambda: StateGraph(SequentialFlowState))

    @classmethod
    def auto(cls, goal: str, roles: Sequence[Role]):
        steps = []
        return Flow(steps=steps)

    def task_wrapper(self, task: Node):
        def execute(state):
            # inject
            if (callback := limit_callback_var.get()) and callback.should_continue is False:
                return

            if isinstance(task, Task):
                role_name = task.role.name
                desc = f"{role_name} Working on {task.description[:10]}..."
            elif isinstance(task, Flow):
                if not task.chain:
                    task.build()
                role_name = task.__class__.__name__
                desc = f"{role_name} Working..."
            else:
                raise ValueError('task is not instance of Task or Flow')
            tracer.log(EventName.task_start, desc)
            assert task.chain
            _input = dict(context=get_context(state, self.task_context_length))
            _output = task.chain.invoke(_input)
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

    def run(self, initial_state=None):
        tracer.log(EventName.flow_start)
        final_state = super().run(initial_state)
        last_context = final_state['contexts'][-1]
        last_output = last_context['task_output']
        return last_output
