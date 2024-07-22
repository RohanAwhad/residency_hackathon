import re
import json
from src.prompting.questions import questions
import ast


def qa_prompt(main_paper, ref_paper_text):
    prompt = f'''
    You are a helpful assistant who answers the given questions based on the main paper and the reference paper text.
    You are given the important points from the main paper that the user is reading and the important points from a reference paper that is mentioned in the main paper.
    
    You need to understand how the reference is related to the main paper. and answer the following questions. Please answer in a concise manner and only based on the given text.
    
    Your answer needs to be short and to the point.
    
    Main Paper:
    {main_paper}
    
    Reference Paper:
    {ref_paper_text}
    
    Question 1. {questions[0]}
    Question 2. {questions[1]}
    Question 3. {questions[2]}
    
    Give the output in the following format as json within three backticks (```json{{}}```), only output the following:
    {{'Question 1': 'Answer 1', 'Question 2': 'Answer 2', 'Question 3': 'Answer 3'}}
    '''
    return prompt


def parse_qa(json_string):
    data = re.findall(r"```json\n(.*?)```", json_string, re.DOTALL)
    data_dict = ast.literal_eval(data[0])
    data_dict = {questions[i]: v for i, (k, v) in enumerate(data_dict.items())}
    return data_dict


summary_generator_prompt = '''
You are a helpful and intelligent assistant who helps the user to understand a given research paper in a concise manner.
Now look at the paper and summarise the paper so that the user is able to understand the main gists of the paper.
Keep the following points in mind while summarising the paper.

1. The main gist of the paper
2. The key points of the paper
3. The novelty of the paper
4. The conclusion of the paper

Make the summary short, easy to understand, and as informative as possible, do not miss out on important details. Do not add anything which is not relevant to the paper.

Research Paper:
{research_paper}

Summary:
'''
