import google.generativeai as genai
import io
import json
import os
import re
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
# Functions
# ===
import dataclasses
import tempfile
import requests
import scipdf

from typing import Optional

import data_models
import db_utils

@dataclasses.dataclass
class ProcessCurrPaperOut:
  url: str
  ref_ids: list[str]

def _get_section_text(sections):
  return '\n\n'.join([f"### {sec['heading'].strip()}\n\n{sec['text'].strip()}\n" for sec in sections])

def process_curr_paper(url: str) -> Optional[ProcessCurrPaperOut]:
  if not url.endswith('.pdf'): url += '.pdf'
  # check if already_processed

  # download pdf
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
  paper = data_models.Papers(
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
    data_models.References(
      referred_by_paper_url = url,
      reference_id = ref['ref_id'],
      referred_sections = json.dumps(ref_id_to_sec_heading[ref['ref_id']]),
      title = ref['title'],
      authors = ref['authors'],
      journal = ref['journal'],
      year = ref['year'],
    )
    for ref in pdf_dict['references']
    if ref['ref_id'] in ref_id_to_sec_heading
  ]

  db_utils.insert_paper_n_references(paper, references)

  return ProcessCurrPaperOut(url, [ref.reference_id for ref in references])


# process reference
import openai
client = openai.OpenAI(api_key=os.environ['TOGETHER_API_KEY'], base_url='https://api.together.xyz/v1')
questions = ['''How does this reference support the current paper's hypothesis or main argument?
What you should focus on while answering: Understanding the role of the reference in supporting the main points of the research paper is crucial. Does it provide foundational theories, corroborate findings, or offer contrasting views that are addressed within the paper?''',
             '''What is the significance of the referenced work in the field, and how current is it?
What you should focus on while answering: Evaluating the relevance and impact of the referenced work helps in understanding its importance. Consider the publication date, the reputation of the authors, and how frequently the work has been cited by other scholars.''',
             '''What methodologies or key findings from the referenced work are relevant to the current study?
What you should focus on while answering : Identifying specific methodologies or findings that are referenced can shed light on the research design, analysis, and conclusions of the current paper. It helps in understanding how the referenced work influences or relates to the study at hand.''']
prompt = '''
You are a helpful assistant who answers the given questions based on the main paper and the reference paper text.
You are given the important points from the main paper that the user is reading and the important points from a reference paper that is mentioned in the main paper.

You need to understand how the reference is related to the main paper. and answer the following questions. Please answer in a concise manner and only based on the given text.

Your answer needs to be short and to the point.

---

# Reference Paper:

## Title: {}

## Paper

{}

---

# Current Paper

{}

---

Question 1. {}
Question 2. {}
Question 3. {}

Give the output in the following format as json within three backticks (```json{{}}```), only output the following:
{{"Question 1": "<answer_1>", "Question 2": "<answer_2>", "Question 3": "<answer_3>"}}
'''

def search_brave(query: str, count: int):
  # web search for reference
  brave_search_url = "https://api.search.brave.com/res/v1/web/search"
  headers = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "X-Subscription-Token": os.environ['BRAVE_SEARCH_AI_API_KEY']
  }
  params = {
    "q": query,
    "count": count,  # Brave Search API allows max 20 results per request
  }
  response = requests.get(brave_search_url, headers=headers, params=params)
  if response.status_code != 200:
    print('Brave search api gave non-200 response:', response.status_code)
    return None
  response = response.json()
  if 'web' not in response or 'results' not in response['web']:
    print('Brave search didn\'t return results\n', response)
    return None
  return response

def get_pdf_url_from_search_results(response):
  for res in response['web']['results']:
    res_url = res['url']
    if 'arxiv.org' in res_url: return re.sub('arxiv.org/abs', 'arxiv.org/pdf', res_url)
    if 'aclanthology.org' in res_url:
      if res_url.endswith('.pdf'): return res_url
      else:
        if res_url[-1] == '/': return res_url[:-1] + '.pdf'
        return res_url + '.pdf'



def process_reference(paper_url: str, ref_id: str) -> Optional[data_models.ProcessRefOut]:
  paper_url = "https://arxiv.org/pdf/1809.05724"
  if not paper_url.endswith('.pdf'): paper_url += '.pdf'

  # check if already processed
  ret: data_models.ProcessRefOut = db_utils.get_processed_reference(paper_url, ref_id)
  if ret: return ret

  # Continue Processing
  info: data_models.RefInfoOut = db_utils.get_reference_info_for_searching(paper_url, ref_id)

  # search db for reference
  paper = db_utils.search_paper_by_title(info.title.strip().lower())
  if not paper:
    query = f'filetype:pdf "{info.title.strip().lower()}"'
    response = search_brave(query, 1)
    if not response:
      query = f'"{info.title.strip().lower()}"'
      response = search_brave(query, count=10)
      if not response: return None
      else:
        ref_url = get_pdf_url_from_search_results(response)
        if not ref_url:
          print('Unable to get paper url from brave search')
          return None
    else:
      ref_url = response['web']['results'][0]['url']

    ref_obj = process_curr_paper(ref_url)
    if not ref_obj:
      print('Error while processing reference paper')
      return None

    ref_url = ref_obj.url

  else:
    ref_url = paper.paper_url

  # data for prompt
  ref = db_utils.read_paper(ref_url)
  sections_json = json.loads(db_utils.read_paper(paper_url).sections_json)
  sections_json = {res['heading']: res['text'] for res in sections_json}
  curr_paper_text = '\n\n'.join([
    f'### Section: {h}\n\n{sections_json[h].strip()}\n'
    for h in info.referred_sections
  ])

  messages = [dict(
    role = 'user',
    content = prompt.format(ref.title, ref.sections_text, curr_paper_text, *questions)
  )]
  max_iterations = 3
  ans = None
  while max_iterations > 0: 
    try:
      res = client.chat.completions.create(
        model='meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo',
        messages=messages,
        max_tokens=1024,
      )
      content = res.choices[0].message.content
      print(content)
      ptrn = re.compile(r'```json(.*?)```', re.DOTALL)
      ans = json.loads(re.search(ptrn, content).group(1))

      assert 'Question 1' in ans
      assert 'Question 2' in ans
      assert 'Question 3' in ans

      break
    except Exception as e:
      print(e)
      max_iterations -= 1
      ans = None

  # save to postgres
  if ans is None:
    print('LLM messed up')
    return None

  q1 = ans['Question 1']
  q2 = ans['Question 2']
  q3 = ans['Question 3']
  db_utils.insert_reference_info(paper_url, ref_id, ref_url, q1, q2, q3)

  return data_models.ProcessRefOut(ref_url, q1, q2, q3)

  


class Paper(BaseModel):
  title: str
  abstract: str
  content: str

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
