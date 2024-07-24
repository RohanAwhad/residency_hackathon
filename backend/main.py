import os
import json
import ast
import functools
import requests
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.prompting.chat_prompt import make_chat_prompt, get_suggestions
from src.processor import process
from src.scraper import download_from_url
import subprocess

## code to run docker containers
# docker run --rm --init --ulimit core=0 -p 8070:8070 --memory=4096m --cpus=4 lfoppiano/grobid:0.8.0
# subprocess.run(['docker', 'run', '-d', '--rm', '--init', '--ulimit', 'core=0', '-p', '8070:8070', '--memory=4096m', '--cpus=4', 'lfoppiano/grobid:0.8.0'], shell=True)
# time.sleep(5)

# Constants
# PAPER_DICT_PATH = './data/paper_metadata.json'
RETRIEVE_URL = 'http://localhost:8002/retrieve'
RESPONSE_URL = 'http://localhost:8001/get_response'

# def load_paper_dict():
#     if os.path.exists(PAPER_DICT_PATH):
#         with open(PAPER_DICT_PATH, 'r') as f:
#             return json.load(f)
#     return {}
#
#
# paper_dict = load_paper_dict()

# FastAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_paper_context(parsed_pdf):
    title = parsed_pdf['title']
    abstract = parsed_pdf['abstract']
    section_data = '\n'.join(f"{section['heading']}\n{section['text']}" for section in parsed_pdf['sections'])
    return f"{title}\n{abstract}\n{section_data}"


@functools.lru_cache(maxsize=128)
def process_paper(paper_url):
    paper_content = download_from_url(paper_url)
    results = process(paper_content, paper_url)
    return results
@app.post("/get_summaries")
def get_summaries(request: dict):
    return process_paper(request['paper_url'])


# @app.post("/get_chat_response")
# def get_chat_response(request: dict):
#     history = request['history']
#     new_message = request['new_message']
#     paper_url = request['paper_url']
#
#     context_response = requests.post(RETRIEVE_URL, json={
#         'query': new_message,
#         'save_path': paper_dict[paper_url]['save_path']
#     }).json()
#
#     context = context_response['context']
#     paper_context = get_paper_context(paper_dict[paper_url]['parsed_pdf'])
#
#     prompt = make_chat_prompt(history, new_message, context, paper_context)
#     response = requests.post(RESPONSE_URL, json={'input_prompt': prompt}).json()['response']
#
#     suggestions = get_suggestions_with_retry(new_message, response)
#
#     return {'new_response': response, 'suggestions': suggestions}


def get_suggestions_with_retry(new_message, response, max_attempts=3):
    suggestion_prompt = get_suggestions(new_message, response)
    for _ in range(max_attempts):
        try:
            suggestions_response = requests.post(RESPONSE_URL, json={'input_prompt': suggestion_prompt}).json()[
                'response']
            suggestions = ast.literal_eval(suggestions_response)
            return [{'suggestion': s} for s in suggestions]
        except:
            pass
    return [{'suggestion': ''}]


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')