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
import dataclasses
import tempfile
import requests
import scipdf

from typing import Optional

import db_models
import db_utils

@dataclasses.dataclass
class ProcessCurrPaperOut:
  url: str
  ref_ids: list[str]

def _get_section_text(sections):
  return '\n\n'.join([f"### {sec['heading'].strip()}\n\n{sec['text'].strip()}\n" for sec in sections])

def process_curr_paper(url: str) -> Optional[ProcessCurrPaperOut]:
  # download pdf
  if not url.endswith('.pdf'): url += '.pdf'
  res = requests.get(url)
  if res.status_code != 200: print('Failed to download PDF at:', url)
  fn = None
  with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
    tmp_file.write(res.content)
    fn = tmp_file.name
  print('PDF downloaded at:', fn)

  # parse pdf
  pdf_dict = scipdf.parse_pdf_to_dict(fn)
  os.remove(fn) # delete tmp file post processing
  paper = db_models.Paper(
    url,
    pdf_dict['title'],
    pdf_dict['authors'],
    pdf_dict['abstract'],
    _get_section_text(pdf_dict['sections']),
    json.dumps(pdf_dict['sections'])
  )

  # parse references
  ref_id_to_sec_heading = {}
  for sec in pdf_dict['sections']:
    for ref_id in sec['publication_ref']:
      if ref_id not in ref_id_to_sec_heading: ref_id_to_sec_heading[ref_id] = []
      ref_id_to_sec_heading[ref_id].append(sec['heading'].strip())

  references = [
    db_models.References(
      referred_by_paper_url = url,
      reference_id = ref['ref_id'],
      referred_sections = json.dumps(ref_id_to_sec_heading[ref['ref_id']])
    )
    for ref in pdf_dict['references']
    if ref['ref_id'] in ref_id_to_sec_heading
  ]

  db_utils.insert_paper(paper)
  db_utils.insert_batch_references(references)

  # return {url: url, ref_ids: [ref_id...]}
  return ProcessCurrPaperOut(url, [ref.reference_id for ref in references])

  



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
  res = model.generate_content([sys_prompt, paper.model_dump_json(indent=2)], stream=True)
  for chunk in res:
    print(chunk.text)
    yield chunk.text
  yield "<|im_end|>"


def generate_code(mindmap):
  model = genai.GenerativeModel(gemini_pro)
  with open(f'{PROMPT_DIR}/paper_to_python_prompt.txt', 'r') as f: sys_prompt = f.read()
  res = model.generate_content([sys_prompt, mindmap], stream=True)
  for chunk in res: yield chunk.text
  yield "<|im_end|>"


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
