from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict

class Paper(BaseModel):
  paper_url: HttpUrl  # primary key
  title: str
  authors: str  # scipdf gives authors in ';' separated string
  abstract: str
  sections: str
  summary_markdown: Optional[str] = None
  code: Optional[str] = None


class References(BaseModel):
  # both urls are foreign keys referring to paper_url in Paper table
  # (referred_by_paper_url, reference_paper_url) are unique
  referred_by_paper_url: HttpUrl
  referred_paper_url: HttpUrl
  q1_answer: Optional[str] = None
  q2_answer: Optional[str] = None
  q3_answer: Optional[str] = None



class Embeddings(BaseModel):
  paper_url: HttpUrl
  chunk: str

class EmbeddingsIn(Embeddings):
  embedding: List[float]  # Vector with 384 dimensions

class EmbeddingsOut(Embeddings):
  sim_score: float
