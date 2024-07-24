import google.generativeai as genai
import io
import json
import os
import requests
import functools

from pydantic import BaseModel
from PyPDF2 import PdfReader

# ===
# Constants
# ===
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
PROMPT_DIR = "prompts"

# ===
# Configure LLMs
# ===
genai.configure(api_key=GEMINI_API_KEY)

# Specify the Gemini-Flash model
gemini_flash = "gemini-1.5-flash"
gemini_pro = "gemini-1.5-pro"

# ===
# Define the Paper class
# ===
class Paper(BaseModel):
  title: str
  abstract: str
  content: str


# ===
# Functions
# ===
@functools.lru_cache(maxsize=128)
def get_paper(url: str) -> Paper:
  """Get the paper title, abstract and content from a given URL."""

  # TODO (rohan): update this to call Mihir's API
  with open('/Users/rohan/1_Project/the_residency_hackathon/sample.json', 'r') as f: data = json.load(f)

  content = []
  for sec in data['sections']:
    heading = sec['heading']
    text = sec['text']
    content.append(f'## {heading}\n{text}')


  return Paper(
    title=data['title'],
    abstract=data['abstract'],
    content='\n\n'.join(content)
  )

def generate_mindmap(paper: Paper):
  model = genai.GenerativeModel(gemini_flash)
  with open(f'{PROMPT_DIR}/paper_to_mindmap_prompt.txt', 'r') as f: sys_prompt = f.read()
  # res = model.generate_content([sys_prompt, paper.model_dump_json(indent=2)], stream=True)
  res = model.generate_content(['What is the meaning of life?'], stream=True)
  for chunk in res:
    print(chunk.text)
    yield chunk.text


def generate_code(mindmap):
  model = genai.GenerativeModel(gemini_pro)
  with open(f'{PROMPT_DIR}/paper_to_python_prompt.txt', 'r') as f: sys_prompt = f.read()
  res = model.generate_content([sys_prompt, mindmap], stream=True)
  for chunk in res: yield chunk.text
  yield 0


# ===
# Utils
# ===
def save_text(text, filename):
  with open(filename, 'w') as f: f.write(text)

def load_text(filename):
  with open(filename, 'r') as f: return f.read()


if __name__ == '__main__':
  paper = get_paper('https://arxiv.org/abs/2106.04561')
  mindmap_iter = generate_mindmap(paper)
  mindmap = []
  for chunk in mindmap_iter:
    if chunk == 0: break
    print(chunk)
    mindmap.append(chunk)
  mindmap = ''.join(mindmap)

  code_iter = generate_code(mindmap)
  code = []
  for chunk in code_iter:
    if chunk == 0: break
    print(chunk)
    code.append(chunk)
  code = ''.join(code)