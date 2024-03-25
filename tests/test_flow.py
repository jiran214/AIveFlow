#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiveflow.flow import list
from aiveflow.role.task import Task


def test_list():
    flow = list.ListFlow(
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