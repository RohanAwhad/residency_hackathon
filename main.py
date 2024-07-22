import os
import json
from fastapi import FastAPI
import requests
from src.prompting.chat_prompt import make_chat_prompt, get_suggestions
import ast
from src.processor import process
from src.scraper import download_from_url
from src.prompting.prompts import parse_qa
import functools

# add cors
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

paper_dict_path = './data/paper_metadata.json'

paper_dict = {}
if os.path.exists(paper_dict_path):
    paper_dict = json.load(open(paper_dict_path, 'r'))


def get_paper_context(parsed_pdf):
    title = parsed_pdf['title']
    abstract = parsed_pdf['abstract']
    section_data = '\n'.join([section['heading'] + '\n' + section['text'] for section in parsed_pdf['sections']])
    context = title + '\n' + abstract + '\n' + section_data
    return context


@functools.lru_cache(maxsize=128)
def temp(paper_url):
    print('condition', paper_url not in paper_dict)
    if paper_url not in paper_dict:
        paper_dict[paper_url] = {}
        paper_dict[paper_url]['save_path'] = download_from_url(paper_url)
        json.dump(paper_dict, open(paper_dict_path, 'w'))

    results = process(paper_dict, paper_url)
    with open(paper_dict_path, 'w') as f:
        json.dump(results, f)
    response = {'paper_url': paper_url, 'summary': results[paper_url]['summary'],
                'qa_for_references': results[paper_url]['qa_for_references']}
    return response


@app.post("/get_summaries")
def get_summaries(request: dict):
    paper_url = request['paper_url']
    return temp(paper_url)


@app.post("/get_chat_response")
def get_chat_response(request: dict):
    history = request['history']
    new_message = request['new_message']
    print('retrieving context')
    context = requests.post('http://localhost:8002/retrieve', json={'query': new_message,
                                                                    'save_path': paper_dict[request['paper_url']][
                                                                        'save_path']}).json()['context']
    prompt = make_chat_prompt(history, new_message, context,
                              get_paper_context(paper_dict[request['paper_url']]['parsed_pdf']))
    print('generating response')
    response = requests.post('http://localhost:8001/get_response', json={'input_prompt': prompt}).json()['response']
    suggestion_prompt = get_suggestions(new_message, response)
    passed = False
    max_attempts = 3
    a = 0
    while not passed:
        try:
            suggestions = \
            requests.post('http://localhost:8001/get_response', json={'input_prompt': suggestion_prompt}).json()[
                'response']
            suggestions = ast.literal_eval(suggestions)
            suggestions = [{'suggestion': s} for s in suggestions]
            passed = True
            a += 1

        except:
            suggestions = [{'suggestion': ''}]
        if a == max_attempts:
            suggestions = [{'suggestion': ''}]
            break
    return {'new_response': response, 'suggestions': suggestions}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='0.0.0.0', port=8000, log_level='info')
