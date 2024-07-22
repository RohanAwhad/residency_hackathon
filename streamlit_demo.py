import os
import json
import streamlit as st
# from src.pdf_parser import parse_pdf, get_all_references, get_section_wise_references
# from src.prompts.make_prompt import qa_prompt
import requests

meta_path = './data/paper_metadata.json'
papers_dir = '../data/papers/'

paper_metadata = {}
if os.path.exists(meta_path):
    paper_metadata = json.load(open(meta_path, 'r'))

st.title("Know your Paper!")

url = st.text_input("Paper URL")
button = st.button("Submit")

if button:
    if url:
        results = requests.post('http://localhost:8000/get_summaries', json={'paper_url': url})
        st.json(results.json())


# question = st.text_input("Question")
# history = '''User : Hi, how are you doing?\n
#            Assistant : I am doing well. How about you?\n
#            User: I would like to know more about the paper.\n
#            Assistant: Sure, what do you want to know?\n'''
#
# button = st.button("Submit")
#
# if button:
#     if question:
#         results = requests.post('https://08f7-24-147-251-136.ngrok-free.app/get_chat_response', json={'new_message': question,
#                                                                                                       'history': history,
#                                                                                                       'paper_url': 'https://arxiv.org/pdf/2006.15720'})
#         st.json(results.json())
#
#

