#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import importlib
import json
import uuid
from _operator import itemgetter
from typing import Optional, Any, Callable, List, TypeVar, Union

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser, BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.tools import BaseTool, tool
from langchain_openai import ChatOpenAI
from pydantic import model_validator, BaseModel, Field, UUID4

from aiveflow import settings
from aiveflow.utils import get_os_language

# https://python.langchain.com/docs/modules/agents/tools/custom_tools#subclass-basetool
ToolLike = TypeVar('ToolLike', Callable[[str], str], str)


class Role(BaseModel):
    name: str = Field(description='role name')
    system: str = Field(description='Role play setting')
    openai_model_name: Optional[str] = None
    tools: List['ToolLike'] = Field([])
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

    # @model_validator(mode='after')
    # def __set_embedchain(self):
    #     if not self.knowledge:
    #         return self
    #     if isinstance(self.knowledge, list):
    #         try:
    #             from aiveflow.knowledge import KnowledgeBase
    #         except ImportError:
    #             raise ImportError('Please run `pip install embedchain`')
    #         _base = KnowledgeBase.get(self.name)
    #         for source in self.knowledge:
    #             tracer.log(EventName.knowledge_learn, source)
    #             _base.add(source)
    #         self.knowledge = EmbedchainRetriever(clinet=_base)
    #     return self

    @property
    def slug(self):
        """ensure role class name unique"""
        return self.__class__.name

    @model_validator(mode='after')
    def __set_chat_model(self):
        self.chat_model = self.chat_model or ChatOpenAI(model_name=self.openai_model_name or settings.OPENAI_MODEL_NAME)
        return self

    def instruct(self, description):
        return Task(role=self, description=description)

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


class Task(Node):
    role: 'Role' = Field(default_factory=lambda: Role(
        name='AI assistant',
        system='You are an AI assistant'
    ))
    description: Optional[str] = None
    output_parser: BaseOutputParser = Field(default_factory=StrOutputParser)
    tools: List[ToolLike] = []

    @model_validator(mode='after')
    def __set_chain(self):
        assert self.chain or self.description, 'Both description and chain are empty!'
        # custom chain
        if self.chain:
            self.chain = self.chain.with_config(tags=['task'])
            return self

        # set llm
        self.chain = self.role.chat_model

        # override if exists
        self.tools = self.tools or self.role.tools
        # load module if tool is str type
        _tools = []
        for _tool in self.tools:
            if isinstance(_tool, str):
                _tool = importlib.import_module(_tool)
            if isinstance(_tool, BaseTool):
                pass
            elif callable(_tool):
                _tool = tool()(_tool)
            else:
                raise ValueError('tool is not type of langchain.BaseTool')
            # if not isinstance(_tool, func):
            #     _tool = tool(_tool)
            _tools.append(_tool)
        self.tools = _tools

        # global var
        if settings.LANGUAGE == 'auto':
            settings.LANGUAGE = get_os_language() or 'Chinese'

        # set prompt
        human_temple = '{knowledge}{task_context}Your task:\n{input}'
        system_temple = f"Your are {self.role.name}\n{self.role.system}\nPlease use {settings.LANGUAGE}."

        try:
            instruction = self.output_parser.get_format_instructions()
            human_temple += f"\n{instruction}"
        except NotImplementedError:
            pass
        _prompt = ChatPromptTemplate.from_messages([
            ('system', system_temple), ('human', human_temple)
        ])

        # construct chain
        if self.tools:
            _prompt += MessagesPlaceholder("agent_scratchpad")
            # set agent, just support openai model
            assert isinstance(self.chain, ChatOpenAI)
            agent = create_openai_tools_agent(self.chain, self.tools, _prompt)
            # Create an agent executor by passing in the agent and tools
            agent_executor = AgentExecutor(agent=agent, tools=self.tools)
            self.chain = agent_executor | itemgetter('output')
        else:
            self.chain = _prompt | self.chain

        self.chain |= self.output_parser

        # inject knowledge
        if self.role.knowledge:
            self.chain = RunnablePassthrough.assign(knowledge=itemgetter('input') | self.role.knowledge) | self.chain
        self.chain = self.chain.with_config(tags=['task'])
        return self

    def run(self, task_context=""):
        return self.chain.invoke({'input': self.description, 'task_context': task_context})

    def __str__(self):
        return f"Task:{self.description[:10]}..."
