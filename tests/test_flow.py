#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

from aiveflow.flow import sequential
from aiveflow.role.task import Task


def test_list():
    flow = sequential.SequentialFlow(
        steps=[
            Task(description='选一个热门话题'),
            Task(description='写一个100字大纲'),
            Task(description='根据大纲写一篇400字的公众号文案，以"感谢读者阅读！"结尾')
        ]
    )
    assert len(flow.steps) == 3
    res = flow.run()
    print(res)
    assert res
    assert '感谢读者阅读' in res


def test_rpm(capsys):
    setattr(time, 'sleep', lambda x: print('waiting...'))
    flow = sequential.SequentialFlow(steps=[Task(description='3+3=?'), Task(description='1+1=?')], max_rpm=1)
    res = flow.run()
    assert '2' in res
    captured = capsys.readouterr()
    assert captured.out.count('waiting...') == 1


def test_limit(capsys):
    flow = sequential.SequentialFlow(steps=[Task(description='1+1=?'), Task(description='3+3=?')], max_token=1)
    res = flow.run()
    assert '2' in res
    captured = capsys.readouterr()
    assert 'exceed' in captured.out