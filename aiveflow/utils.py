#!/usr/bin/env python
# -*- coding: utf-8 -*-
import locale
import pycountry


def get_os_language():
    try:
        loc = locale.getdefaultlocale()[0]
        return pycountry.languages.get(alpha_2=loc.split('_')[0]).name
    except:
        return