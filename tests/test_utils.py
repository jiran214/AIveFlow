#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiveflow import utils


def test_lang():
    assert utils.get_os_language().lower() == 'chinese'