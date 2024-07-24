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

db_utils.insert_reference_answers(ref)
print(db_utils.get_references_of_paper(url))

