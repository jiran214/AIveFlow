#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

from aiveflow.role.core import Role


class RoleRepository:
    """
    - 连接外部role数据源，将设定保存在本地
    - 加载本地的role config数据到RoleManger
    """
    role_map = {}

    def load(self, with_embed=False) -> List[Role]:
        """第一次加载会持久化存储到本地"""
        ...

    def pull(self):
        ...

    def update(self):
        ...

    def delete(self):
        ...


class AwesomeChatgptPrompts(RoleRepository):
    ...

