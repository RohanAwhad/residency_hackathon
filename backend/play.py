import db_utils
import db_models
import scipdf

def get_section_text(sections):
  return '\n\n'.join([f"### {sec['heading']}\n\n{sec['text']}\n" for sec in sections])

url = "https://arxiv.org/pdf/1801.03924v2"
'''
a = scipdf.parse_pdf_to_dict("/Users/rohan/Downloads/1801.03924v2.pdf")


paper = db_models.Paper(
  paper_url = url,
  title = a['title'],
  authors = a['authors'],
  abstract = a['abstract'],
  sections = get_section_text(a['sections']),
)
  
db_utils.insert_paper(paper)
'''

db_utils.insert_summary(url, "This is a summary")
db_utils.insert_code(url, "this is code blah")
print(db_utils.read_paper(url))
