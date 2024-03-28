#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import json
import uuid
from typing import Optional, Any, Callable, List, TypeVar, Union

from langchain.chains.base import Chain
from langchain_community.retrievers.embedchain import EmbedchainRetriever
from langchain_core.language_models import BaseChatModel
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import model_validator, BaseModel, Field, UUID4

from aiveflow import settings
from aiveflow.callbacks import tracer
from aiveflow.utils import EventName

# https://python.langchain.com/docs/modules/agents/tools/custom_tools#subclass-basetool
ToolLike = TypeVar('ToolLike', Callable[[str], str], str)


class Role(BaseModel):
    name: str = Field(description='role name')
    system: str = Field(description='Role play setting')
    tools: List['ToolLike'] = Field([])
    openai_model_name: Optional[str] = None
    chat_model: Optional[BaseChatModel] = None
    knowledge: Optional[Union[BaseRetriever, List[str]]] = None

    @classmethod
    def from_json(cls, filepath):
        assert '.json' in filepath
        # 读取和解析JSON文件
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert isinstance(data, dict), 'json should be a object which include name, system key'
        return cls(**data)

    @model_validator(mode='after')
    def __set_embedchain(self):
        if not self.knowledge:
            return self
        if isinstance(self.knowledge, list):
            try:
                from aiveflow.knowledge import KnowledgeBase
            except ImportError:
                raise ImportError('Please run `pip install embedchain`')
            _base = KnowledgeBase.get(self.name)
            for source in self.knowledge:
                tracer.log(EventName.knowledge_learn, source)
                _base.add(source)
            self.knowledge = EmbedchainRetriever(clinet=_base)
        return self

    @property
    def slug(self):
        """ensure role class name unique"""
        return self.__class__.name

    @model_validator(mode='after')
    def __set_chat_model(self):
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
        return self.id

    class Config:
        arbitrary_types_allowed = True
