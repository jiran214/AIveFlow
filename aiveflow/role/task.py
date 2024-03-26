#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import uuid
from _operator import itemgetter
from typing import Optional, List, Sequence

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.tools import tool, BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, model_validator, UUID4

from aiveflow import settings
from aiveflow.role.core import Role, ToolLike
from aiveflow.role.groups import DEFAULT_AI_ROLE


class Task(BaseModel):
    role: Role = Field(default_factory=lambda: DEFAULT_AI_ROLE)
    description: Optional[str] = None
    tools: List[ToolLike] = []
    chain: Optional[Runnable] = None
    id: UUID4 = Field(default_factory=uuid.uuid4, frozen=True)

    @model_validator(mode='after')
    def __set_chain(self):
        assert self.chain or self.description, 'Both description and chain are empty!'
        # custom chain
        if self.chain:
            return self

        # set llm
        self.role.set_chat_model()
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

        # set prompt
        _prompt = ChatPromptTemplate.from_messages([
            ('system', f"{self.role.system}\nPlease use {settings.LANGUAGE}."),
            ('human', '{context}Your task:\n' + self.description)
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
            self.chain = _prompt | self.chain | StrOutputParser()
        return self

    @property
    def node_key(self):
        return str(self)

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return f"{self.id}:{self.role.name}:{self.description[:10]}..."


class __RouteTask(Task):
    role: Optional[Role] = None
    roles: Sequence[Role]

    def route(self):
        ...
        return self.roles[0]