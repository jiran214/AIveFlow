#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from aiveflow.role.core import Role
from aiveflow.role.task import Task


def search(query: str):
    """
    use for solving problem
    Args:
        query: search input

    Returns:
        result
    """
    return 'no result'


def test_role_init():
    researcher = Role(name='researcher', system='You are a researcher', tools=[search], openai_model_name='gpt-4')
    assert researcher.name == 'researcher'
    assert researcher.system == 'You are a researcher'
    assert researcher.tools == [search]
    assert isinstance(researcher.chat_model, ChatOpenAI)


def test_task_init():
    researcher = Role(name='researcher', system='You are a researcher', tools=[search])
    task = Task(role=researcher, description='给我几个关于"科技"的话题', tools=[search])
    assert not task.chain
    task.prepare_execute()
    assert task.chain


def test_agent_execute():
    researcher = Role(name='researcher', system='You are a researcher', tools=[search])
    task = Task(role=researcher, description='给我几个关于"科技"的话题', tools=[search])
    task.prepare_execute()
    res = task.chain.invoke({'context': ''})
    # print(res)
    assert res


def test_model_execute():
    researcher = Role(name='researcher', system='You are a researcher')
    task = Task(role=researcher, description='给我几个关于"科技"的话题')
    task.prepare_execute()
    res = task.chain.invoke({'context': ''})
    print(res)
    assert res
