#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiveflow import utils, settings
from aiveflow.callbacks import limit_callback_var, TokenLimitCallback, tracer, trace_callback_var
from aiveflow.utils import EventName


def test_lang():
    assert utils.get_os_language().lower() == 'chinese'


def test_limit_callback_var():

    def f():
        return limit_callback_var.get() is callback

    callback = TokenLimitCallback(max_token=10)
    limit_callback_var.set(callback)
    assert limit_callback_var.get() is callback
    assert limit_callback_var.get().should_continue == True
    assert f()


def test_trace_callback_var(capsys):
    tracer.log(EventName.flow_start, 'start')
    captured = capsys.readouterr()
    assert EventName.flow_start.value not in captured.out

    trace_callback_var.set(tracer)
    tracer.log(EventName.flow_start, 'start')
    captured = capsys.readouterr()
    assert EventName.flow_start.value in captured.out

    trace_callback_var.set(None)
    tracer.log(EventName.flow_start, 'start')
    captured = capsys.readouterr()
    assert EventName.flow_start.value not in captured.out


def test_tracer(capsys):
    tracer.log(EventName.flow_start, 'start')
    captured = capsys.readouterr()
    assert EventName.flow_start.value in captured.out

    tracer.log(EventName.task_start, 'desc')
    assert tracer.status

    tracer.log(EventName.task_output, 'desc', 'output')
    captured = capsys.readouterr()
    assert EventName.task_output.value in captured.out
    assert 'output' in captured.out

    tracer.log(EventName.tool_use, 'desc')
    captured = capsys.readouterr()
    assert EventName.tool_use.value in captured.out
    assert 'desc' in captured.out

    tracer.log(EventName.tool_output, 'desc', 'output')
    captured = capsys.readouterr()
    assert EventName.tool_output.value in captured.out
    assert 'output' in captured.out
