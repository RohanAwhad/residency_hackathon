import os
import json
import requests

import db_utils
import data_models
import utils

import time
start = time.monotonic()

url = "https://arxiv.org/pdf/1809.05724"
ref_id = 'b19'
print(utils.process_reference(url, ref_id))
end = time.monotonic()
print(f'Total time taken: {end-start} secs')
exit(0)


if not url.endswith('.pdf'): url += '.pdf'

sections_json = json.loads(db_utils.read_paper(url).sections_json)
sections_json = {res['heading']: res['text'] for res in sections_json}


ref_id = 'b24'

info: data_models.RefInfoOut = db_utils.get_reference_info_for_searching(url, ref_id)
curr_paper_text = '\n\n'.join([
  f'### Section: {h}\n\n{sections_json[h].strip()}\n'
  for h in info.referred_sections
])

print(curr_paper_text)

# Brave search
brave_search_url = "https://api.search.brave.com/res/v1/web/search"
headers = {
  "Accept": "application/json",
  "Accept-Encoding": "gzip",
  "X-Subscription-Token": os.environ['BRAVE_SEARCH_AI_API_KEY']
}
query = f'filetype:pdf "{info.title.strip().lower()}"'
params = {
  "q": query,
  "count": 20,  # Brave Search API allows max 20 results per request
}

'''
#response = requests.get(brave_search_url, headers=headers, params=params)
if response.status_code == 200:
  results = response.json()['web']['results']
  if len(results):
    ret = utils.process_curr_paper(results[0]['url'])
    print('Reference Paper processed:', ret)
'''

ref_url = "https://arxiv.org/pdf/1512.08849.pdf"
ref = db_utils.read_paper(ref_url)


questions = ['''How does this reference support the current paper's hypothesis or main argument?
What you should focus on while answering: Understanding the role of the reference in supporting the main points of the research paper is crucial. Does it provide foundational theories, corroborate findings, or offer contrasting views that are addressed within the paper?''',
             '''What is the significance of the referenced work in the field, and how current is it?
What you should focus on while answering: Evaluating the relevance and impact of the referenced work helps in understanding its importance. Consider the publication date, the reputation of the authors, and how frequently the work has been cited by other scholars.''',
             '''What methodologies or key findings from the referenced work are relevant to the current study?
What you should focus on while answering : Identifying specific methodologies or findings that are referenced can shed light on the research design, analysis, and conclusions of the current paper. It helps in understanding how the referenced work influences or relates to the study at hand.''']

prompt = f'''
You are a helpful assistant who answers the given questions based on the main paper and the reference paper text.
You are given the important points from the main paper that the user is reading and the important points from a reference paper that is mentioned in the main paper.

You need to understand how the reference is related to the main paper. and answer the following questions. Please answer in a concise manner and only based on the given text.

Your answer needs to be short and to the point.

---

# Reference Paper:

## Title: {ref.title}

## Paper

{ref.sections_text}

---

# Current Paper

{curr_paper_text}

---

Question 1. {questions[0]}
Question 2. {questions[1]}
Question 3. {questions[2]}

Give the output in the following format as json within three backticks (```json{{}}```), only output the following:
{{'Question 1': '<answer_1>', 'Question 2': '<answer_2>', 'Question 3': '<answer_3>'}}
'''

import openai
client = openai.OpenAI(api_key=os.environ['TOGETHER_API_KEY'], base_url='https://api.together.xyz/v1')
res = client.chat.completions.create(
  model='meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo',
  messages=[{'role': 'user', 'content': prompt}],
  max_tokens=512,
)
print(res)
import re
ptrn = re.compile(r'```json(.*?)```', re.DOTALL)
match = re.search(ptrn, res.choices[0].message.content)
if not match: print('Failed to generate JSON within triple backticks')
else:
  ans = json.loads(match.group(1))
  print(json.dumps(ans, indent=2))


end = time.monotonic()
print(f'Total time taken: {end-start} secs')


'''
the flow of references:
- get paper_url and ref_id
- get the reference paper info from db
- get the url for the paper from web search or db search
- download the paper and process it using the process_curr_paper funct
- get the sections of the text from the original paper where this paper is referred
- Prompt the LLM to start generating answers for questions based on the context provided
- Stream the output back to the client, with appropriate formatting based on which question is answered and all
'''
