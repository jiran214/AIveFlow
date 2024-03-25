#!/usr/bin/env python
# -*- coding: utf-8 -*-
import locale
import threading
import time
from typing import Optional

import pycountry
from langchain_core.callbacks import BaseCallbackHandler
from pydantic import PrivateAttr, Field, BaseModel, model_validator


def get_os_language():
    try:
        loc = locale.getdefaultlocale()[0]
        return pycountry.languages.get(alpha_2=loc.split('_')[0]).name
    except:
        return


class RPMController(BaseModel):
    max_rpm: int
    _current_rpm: int = PrivateAttr(default=0)
    _timer: Optional[threading.Timer] = PrivateAttr(default=None)
    _lock: threading.Lock = PrivateAttr(default=None)

    def reset(self):
        self._lock = threading.Lock()
        self._reset_request_count()

    def exit(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def check_or_wait(self):
        with self._lock:
            if self._current_rpm < self.max_rpm:
                self._current_rpm += 1
            else:
                print("Max RPM reached, waiting for next minute to start.")
                self._wait_for_next_minute()
                self._current_rpm = 1

    def _wait_for_next_minute(self):
        time.sleep(60)
        self._current_rpm = 0

    def _reset_request_count(self):
        with self._lock:
            self._current_rpm = 0
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(60.0, self._reset_request_count)
        self._timer.start()