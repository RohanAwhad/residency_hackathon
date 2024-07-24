from typing import List
from pydantic.dataclasses import dataclass


@dataclass
class RefEmbeddings:
    ref_id: str
    chunk: str
    embeddings: List[float]
