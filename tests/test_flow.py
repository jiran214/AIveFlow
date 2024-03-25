#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from aiveflow import settings
from aiveflow.components import RPMCallback
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


def test_rpm(capsys):
    settings.set_max_rpm(1)
    assert settings._rpm_controller
    setattr(time, 'sleep', lambda x: print('waiting...'))
    settings._rpm_controller.check_or_wait()
    settings._rpm_controller.check_or_wait()
    RPMCallback().on_chat_model_start()
    res = list.ListFlow(steps=[Task(description='1+1=?')]).run()
    assert '2' in res
    # print('res', res)
    captured = capsys.readouterr()
    assert captured.out.count('waiting...') == 3
    settings._rpm_controller.exit()