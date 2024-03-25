#!/usr/bin/env python
# -*- coding: utf-8 -*-
from langchain_core.callbacks import BaseCallbackHandler

from aiveflow import settings


class RPMCallback(BaseCallbackHandler):
    def on_chat_model_start(self, *args, **kwargs):
        if settings._rpm_controller:
            settings._rpm_controller.check_or_wait()


