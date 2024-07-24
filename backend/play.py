import db_utils
import db_models
import scipdf

def get_section_text(sections):
  return '\n\n'.join([f"### {sec['heading']}\n\n{sec['text']}\n" for sec in sections])

url = "https://arxiv.org/pdf/1801.03924v2"
url2 = 'https://arxiv.org/pdf/rohan'

paper2 = db_models.Paper(
  paper_url = url2,
  title = "Rohan's dummy paper",
  authors = "Rohan",
  abstract = "Blah",
  sections = "### Big Blah\n\nSmall Blah\n",
)
#db_utils.insert_paper(paper2)

ref = db_models.References(
  referred_by_paper_url = url,
  referred_paper_url = url2
)

#db_utils.insert_reference(ref)

ref.q1_answer = "This is answer to Q1"
ref.q2_answer = "This is answer to Q2"
ref.q3_answer = "This is answer to Q3"

#db_utils.insert_reference_answers(ref)
#print(db_utils.get_references_of_paper(url))

import requests
import json

# Define the URL and headers
embedding_url = 'https://fun-sentence-embedder-c8f3c4818216.herokuapp.com/embed_batch'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

# Define the data to be sent
data = [
    "this is string 1",
    "this is string 2",
    "this is string 3",
]

# Perform the POST request
response = requests.post(embedding_url, headers=headers, data=json.dumps(data))

# Print the response
embeddings = response.json()['embeddings']
print(embeddings[0][:3])

embds = []
embds.append(db_models.EmbeddingsIn(
  paper_url = url,
  chunk = "this is string 1",
  embedding = embeddings[0],
))
embds.append(db_models.EmbeddingsIn(
  paper_url = url,
  chunk = "this is string 2",
  embedding = embeddings[1],
))

#db_utils.insert_batch_embeddings(embds)

print(db_utils.get_top_k_similar(embeddings[0], [url], 2))
print(db_utils.get_top_k_similar(embeddings[2], [url], 1))
