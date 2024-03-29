#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiveflow import Role, Task, SequentialFlow


class Team:
    role1 = Role(system='<role play prompt>')
    role2 = ...
    role3 = ...


def get_steps(goal):
    task1 = Task(role=Team.role1, description='<task prompt>')
    task2 = ...
    task3 = ...
    return [task1, task2, task3]


if __name__ == '__main__':
    GOAL = '<your goal>'
    flow = SequentialFlow(steps=get_steps(GOAL), log=True)
    flow.run()

    # future
    # flow = SequentialFlow.auto(GOAL)
