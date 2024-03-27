#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import json
import uuid
from typing import Optional, Any, Callable, List, TypeVar

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import model_validator, BaseModel, Field, UUID4

from aiveflow import settings

# https://python.langchain.com/docs/modules/agents/tools/custom_tools#subclass-basetool
ToolLike = TypeVar('ToolLike', Callable[[str], str], str)


class Role(BaseModel):
    name: str = Field(description='role name')
    system: str = Field(description='Role play setting')
    tools: List['ToolLike'] = Field([])
    openai_model_name: Optional[str] = None
    chat_model: Optional[BaseChatModel] = None

    @classmethod
    def from_json(cls, filepath):
        assert '.json' in filepath
        # 读取和解析JSON文件
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert isinstance(data, dict), 'json should be a object which include name, system key'
        return cls(**data)

    def set_chat_model(self):
        self.chat_model = self.chat_model or ChatOpenAI(model_name=self.openai_model_name or settings.OPENAI_MODEL_NAME)
        return self

    def __str__(self):
        return self.name

    class Config:
        arbitrary_types_allowed = True


class Node(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4, frozen=True)
    chain: Optional[Runnable] = None

    @property
    def node_key(self):
        return str(self)

    @abc.abstractmethod
    def run(self, input): ...

    class Config:
        arbitrary_types_allowed = True
