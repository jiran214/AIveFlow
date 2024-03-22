#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
from _operator import itemgetter
from typing import Optional, List, Sequence

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, PrivateAttr

from aiveflow import settings
from aiveflow.role.core import Role, ToolLike


class Task(BaseModel):
    role: Role
    description: Optional[str] = None
    tools: List[ToolLike] = []
    chain: Optional[Runnable] = None
    _output: str = PrivateAttr()

    def prepare_execute(self):
        # override if exists
        self.tools = self.tools or self.role.tools
        # custom chain
        if self.chain:
            return
        # set prompt
        _prompt = ChatPromptTemplate.from_messages([
            ('system', f"{self.role.system}\nPlease use {settings.LANGUAGE}."),
            ('human', '{input}')
        ])

        # set llm
        self.chain = self.role.chat_model
        # construct chain
        if self.tools:
            # set agent, just support openai model
            assert isinstance(self.chain, ChatOpenAI)
            # load module if tool is str type
            self.tools = [importlib.import_module(_tool) if isinstance(_tool, str) else _tool for _tool in self.tools ]
            agent = create_openai_tools_agent(self.chain, self.tools, _prompt)
            # Create an agent executor by passing in the agent and tools
            agent_executor = AgentExecutor(agent=agent, tools=self.tools)
            self.chain = agent_executor | itemgetter('output')
        else:
            self.chain = _prompt | self.chain | StrOutputParser()

    @property
    def output(self):
        return self._output

    class Config:
        arbitrary_types_allowed = True


class RouteTask(Task):
    role: Optional[Role] = None
    roles: Sequence[Role]

    def route(self):
        ...
        return self.roles[0]

    def prepare_execute(self):
        self.role = self.route()
        super().prepare_execute()