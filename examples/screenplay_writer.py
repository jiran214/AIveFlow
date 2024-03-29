#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aiveflow import Role, RolePlay, Task, SequentialFlow

analyst = Role(
    name='analyse',
    system=RolePlay(
        goal='''You will distill all arguments from all discussion members. Identify who said what. You can reword what they said as long as the main discussion points remain.''',
        backstory='You are an expert discussion analyst.'
    )
)

scriptwriter = Role(
    name='scriptwriter',
    system=RolePlay(
        goal='Turn a conversation into a movie script. Only write the dialogue parts. Do not start the sentence with an action. Do not specify situational descriptions. Do not write parentheticals.',
        backstory='''You are an expert on writing natural sounding movie script dialogues. You only focus on the text part and you HATE directional notes.'''
    )

)

formatter = Role(
    name='formatter',
    system=RolePlay(
        goal='''Format the text as asked. Leave out actions from discussion members that happen between brackets, eg (smiling).''',
        backstory='You are an expert text formatter.'
    )
)

scorer = Role(
    name='scorer',
    system=RolePlay(
        goal='''You score a dialogue assessing various aspects of the exchange between the participants using a 1-10 scale, where 1 is the lowest performance and 10 is the highest:
Scale:
1-3: Poor - The dialogue has significant issues that prevent effective communication.
4-6: Average - The dialogue has some good points but also has notable weaknesses.
7-9: Good - The dialogue is mostly effective with minor issues.
10: Excellent - The dialogue is exemplary in achieving its purpose with no apparent issues.
Factors to Consider:
Clarity: How clear is the exchange? Are the statements and responses easy to understand?
Relevance: Do the responses stay on topic and contribute to the conversation's purpose?
Conciseness: Is the dialogue free of unnecessary information or redundancy?
Politeness: Are the participants respectful and considerate in their interaction?
Engagement: Do the participants seem interested and actively involved in the dialogue?
Flow: Is there a natural progression of ideas and responses? Are there awkward pauses or interruptions?
Coherence: Does the dialogue make logical sense as a whole?
Responsiveness: Do the participants address each other's points adequately?
Language Use: Is the grammar, vocabulary, and syntax appropriate for the context of the dialogue?
Emotional Intelligence: Are the participants aware of and sensitive to the emotional tone of the dialogue?''',
        backstory='You are an expert at scoring conversations on a scale of 1 to 10.'
    )
)


def get_steps(discussion):
    # process post with a crew of agents, ultimately delivering a well formatted dialogue
    task1 = analyst.instruct(
        description='Analyse in much detail the following discussion:\n### DISCUSSION:\n' + discussion,
    )
    task2 = scriptwriter.instruct(
        description='Create a dialogue heavy screenplay from the discussion, between people. Do NOT write parentheticals. Leave out wrylies. You MUST SKIP directional notes.',
    )
    task3 = formatter.instruct(
        description='''Format the script exactly like this:
    ## (person 1):
    (first text line from person 1)
    
    ## (person 2):
    (first text line from person 2)
    
    ## (person 1):
    (second text line from person 1)
    
    ## (person 2):
    (second text line from person 2)''',
    )
    return [task1, task2, task3]


def get_comment(screenplay):
    comment = scorer.instruct(
        description='Read the dialogue. Then score the script on a scale of 1 to 10. Only give the score as a number, nothing else. Do not give an explanation.',
    ).run(task_context=f"DIALOGUE: {screenplay}\n")
    print(comment)
    return comment


if __name__ == '__main__':
    DISCUSSION = 'xxx'
    flow = SequentialFlow(steps=get_steps(DISCUSSION), log=True)
    screenplay = flow.run()
    # get_comment(get_comment)




