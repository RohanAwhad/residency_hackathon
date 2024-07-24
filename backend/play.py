import db_utils
import db_models
import scipdf

url = "https://arxiv.org/pdf/1801.03924v2"
a = scipdf.parse_pdf_to_dict("/Users/rohan/Downloads/1801.03924v2.pdf")

def get_section_text(sections):
  return '\n\n'.join([f"### {sec['heading']}\n\n{sec['text']}\n" for sec in sections])

paper = db_models.Paper(
  paper_url = url,
  title = a['title'],
  authors = a['authors'],
  abstract = a['abstract'],
  sections = get_section_text(a['sections']),
)
  
db_utils.insert_paper(paper)
