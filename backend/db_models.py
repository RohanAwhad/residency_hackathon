from pydantic import BaseModel

'''
title
abstract
sections
  - section heading: text
- references: list
  - title
    year
    journal
    authors
    id
'''

class Paper(BaseModel):
  paper_url: str
  title: str
  abstract: str
  sections: str
  markdown_summary: str
  code: str
