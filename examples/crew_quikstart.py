#!/usr/bin/env python
# -*- coding: utf-8 -*-
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

from aiveflow.flow.list import ListFlow
from aiveflow.role.core import Role
from aiveflow.role.task import Task


def Prompt(role, backstory, goal):
    return f"You are {role}.\n{backstory}\n\nYour personal goal is: {goal}"


os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
search_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

# Define your agents with roles and goals
researcher = Role(
    system=Prompt(
        role='Senior Research Analyst',
        goal='Uncover cutting-edge developments in AI and data science',
        backstory="""You work at a leading tech think tank.
Your expertise lies in identifying emerging trends.
You have a knack for dissecting complex data and presenting actionable insights.""",
    ),
    tools=[search_tool]
)

writer = Role(
    system=Prompt(
        role='Tech Content Strategist',
        goal='Craft compelling content on tech advancements',
        backstory="""You are a renowned Content Strategist, known for your insightful and engaging articles.
You transform complex concepts into compelling narratives."""
    )
)

# Create tasks for your agents
task1 = Task(
    description="""Conduct a comprehensive analysis of the latest advancements in AI in 2024.
Identify key trends, breakthrough technologies, and potential industry impacts.
Expected Full analysis report in bullet points""",
    role=researcher
)

task2 = Task(
    description="""Using the insights provided, develop an engaging blog
post that highlights the most significant AI advancements.
Your post should be informative yet accessible, catering to a tech-savvy audience.
Make it sound cool, avoid complex words so it doesn't sound like AI.
Expected Full blog post of at least 4 paragraphs""",
    role=writer
)

# Instantiate your crew with a sequential process
crew_copy = ListFlow(steps=[task1, task2])

# Get your crew to work!
result = crew_copy.run()

print("######################")
print(result)
