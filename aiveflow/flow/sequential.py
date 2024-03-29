#!/usr/bin/env python
# -*- coding: utf-8 -*-
import operator
from typing import List, TypedDict, Annotated, Optional

from langgraph.graph import StateGraph, END
from pydantic import Field

from aiveflow import settings
from aiveflow.callbacks import limit_callback_var, tracer
from aiveflow.flow.base import Flow
from aiveflow.role.task import Task
from aiveflow.utils import EventName, Stop


class TaskState(TypedDict):
    role_name: str
    task_output: str
    # tools_used: List[str]


class SequentialFlowState(TypedDict):
    contexts: Annotated[List[TaskState], operator.add]


def get_context(state: SequentialFlowState, length):
    if state['contexts']:
        return "This is the context you're working with:\n" + '\n'.join(
            settings.ROLE_CONTEXT_PROMPT.format(role=task['role_name'], task_output=task['task_output'])
            for task in state['contexts'][-length:]
        ) + '\n'
    return ""


class SequentialFlow(Flow):
    steps: List['Task']
    task_context_length: int = 1
    graph: StateGraph = Field(default_factory=lambda: StateGraph(SequentialFlowState))

    def on_task_start(self, state: SequentialFlowState, task: Task) -> dict:
        if (callback := limit_callback_var.get()) and callback.should_continue is False:
            raise Stop
        desc = f"{task.role.name} Working on {task.description[:10]}..."
        tracer.log(EventName.task_start, desc)
        return {
            'input': task.description,
            'task_context': get_context(state, self.task_context_length)
        }

    def on_task_end(self, task_output, task: Task) -> Optional[dict]:
        return {'contexts': [TaskState(role_name=task.role.name, task_output=task_output)]}

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
