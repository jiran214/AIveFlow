#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiveflow import Role, RolePlay, Task, SequentialFlow


class GameCompany:
    senior_engineer = Role(
        name='Senior Software Engineer',
        system=RolePlay(
            goal='Create software as needed',
            backstory=(
                "You are a Senior Software Engineer at a leading tech think tank."
                "Your expertise in programming in python. and do your best to"
                "produce perfect code"
            )
        )
    )

    qa_engineer = Role(
        name='Software Quality Control Engineer',
        system=RolePlay(
            goal='create prefect code, by analizing the code that is given for errors',
            backstory=(
                "You are a software engineer that specializes in checking code for errors. "
                "You have an eye for detail and a knack for finding hidden bugs."
                "You check for missing imports, variable declarations, mismatched"
                "brackets and syntax errors."
                "You also check for security vulnerabilities, and logic errors"
            )
        )
    )

    chief_qa_engineer = Role(
        name='Chief Software Quality Control Engineer',
        system=RolePlay(
            goal='Ensure that the code does the job that it is supposed to do',
            backstory=(
                "You feel that programmers always do only half the job, so you are"
                "super dedicate to make high quality code."
            )
        )
    )


def get_steps(game):
    code_task = Task(
        role=GameCompany.senior_engineer,
        description=(
            "You will create a game using python, these are the instructions:\n"
            "Instructions\n"
            "------------\n"
            f"{game}\n"
            "Your Final answer must be the full python code, only the python code and nothing else."
        )
    )
    review_task = Task(
        role=GameCompany.qa_engineer,
        description=(
            "You are helping create a game using python, these are the instructions:\n"
            "Instructions\n"
            "------------\n"
            f"{game}\n"
            "Using the code you got, check for errors. "
            "Check for logic errors,syntax errors, missing imports, variable declarations, mismatched brackets, "
            "and security vulnerabilities."
            "Your Final answer must be the full python code, only the python code and nothing else."
        )
    )
    evaluate_task = Task(
        agent=GameCompany.chief_qa_engineer,
        description=(
            "You are helping create a game using python, these are the instructions:\n"
            "Instructions\n"
            "------------\n"
            f"{game}\n"
            "You will look over the code to insure that it is complete and does the job that it is supposed to do.\n"
            "Your Final answer must be the full python code, only the python code and nothing else."
        ),
    )
    return [code_task, review_task, evaluate_task]


if __name__ == '__main__':
    GAME_DESCRIPTION = 'Gluttonous snake'
    flow = SequentialFlow(steps=get_steps(GAME_DESCRIPTION), log=True)
    flow.run()

