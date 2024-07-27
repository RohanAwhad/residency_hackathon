import dataclasses
from typing import Optional, List, Dict

@dataclasses.dataclass
class Paper:
  paper_url: str  # primary key
  title: str
  authors: str  # scipdf gives authors in ';' separated string
  abstract: str
  sections_text: str
  sections_json: str
  summary_markdown: Optional[str] = None
  code: Optional[str] = None


@dataclasses.dataclass
class References:
  # both urls are foreign keys referring to paper_url in Paper table
  # (referred_by_paper_url, reference_paper_url) are unique
  referred_by_paper_url: str  # current paper url
  reference_id: str  # provided by parsed version of current paper
  referred_sections: str  # list of json objs {"heading": "..."}

  # useful info for searching and downloading the paper
  title: str
  authors: str
  journal: str
  year: str

  # main info that is required
  referred_paper_url: Optional[str] = None  # will add it as we search it
  q1_answer: Optional[str] = None
  q2_answer: Optional[str] = None
  q3_answer: Optional[str] = None



@dataclasses.dataclass
class Embeddings:
  paper_url: str
  chunk: str

@dataclasses.dataclass
class EmbeddingsIn(Embeddings):
  embedding: List[float]  # Vector with 384 dimensions

@dataclasses.dataclass
class EmbeddingsOut(Embeddings):
  sim_score: float

