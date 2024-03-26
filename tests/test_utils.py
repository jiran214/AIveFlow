#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiveflow import utils
from aiveflow.components import limit_callback_var, TokenLimitCallback


def test_lang():
    assert utils.get_os_language().lower() == 'chinese'


def test_limit_callback_var():
    callback = TokenLimitCallback(max_token=10)
    limit_callback_var.set(callback)
    assert limit_callback_var.get() is callback
    assert limit_callback_var.get().should_continue == True