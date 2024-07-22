import re
import json
from src.prompting.questions import questions
import ast
def qa_prompt(ref_dict, ref_section, section_text):
    reference_text = '\n'.join([section['heading'] + '\n' + section['text']
                                for section in ref_dict['sections']])
    prompt = f'''
    The following reference was found in the ##{ref_section}## section of the paper.

    ### Reference Title: {ref_dict['title']}
    ### Reference Text: {reference_text}

    Now, try to understand the reference given the context it was mentioned in and answer the questions given. The reference was mentioned in the following section -
    Write very concise answers so as to make it easy to understand.
    ### Section Text: 
    {section_text}
    
    Question 1. {questions[0]}
    Question 2. {questions[1]}
    Question 3. {questions[2]}
    
    Give the output in the following format as json, only output the following:
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