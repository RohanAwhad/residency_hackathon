from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

import data_models
import db_utils
import utils

app = FastAPI()
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/")
def read_root():
  return {"Hello": "World"}

# process paper
@app.get('/process_paper')
def process_paper(paper_url: str):
  ret = utils.process_curr_paper(paper_url)
  if ret: return ret
  raise HTTPException(status_code=500, detail="Couldn't process current paper")

# process reference
@app.get('/process_reference')
def process_reference(paper_url: str, ref_id: str):
  ret = utils.process_reference(paper_url, ref_id)
  if ret: return ret
  raise HTTPException(status_code=500, detail="Couldn't generate information about this reference")

# chat
class Message(BaseModel):
  role: str
  content: str

class ChatReqIn(BaseModel):
  paper_url: HttpUrl
  messages: list[data_models.Message]

@app.post('/chat/response')
def generate_chat_response(inp: ChatReqIn):
  query = inp.messages[-1].content
  query_embeddings = utils.embed([query], mode='query')
  if query_embeddings is None: raise HTTPException(status_code=500, detail='Couldn\'t generate embeddings from user message')
  query_embeddings = query_embeddings[0]

  paper_url = str(inp.paper_url)
  if not paper_url.endswith('.pdf'): paper_url += '.pdf'
  ref_urls = db_utils.get_reference_urls(paper_url)
  if ref_urls is None:
    print('Couldn\'t find any reference paper urls')
    ref_urls = []

  ref_urls.append(paper_url)
  context = db_utils.get_top_k_similar(query_embeddings, ref_urls, 3)
  if context is None: print('Couldn\'t retrieve context')
  response = utils.generate_chat_response(context, inp.messages)
  return response


class StreamOut(BaseModel):
  chunk: str
  is_done: bool

mindmap_chunks = ''
def stream_response(iter, callable):  # callable is the function that will be called after all chunks are sent to save it in DB
  if mindmap_chunks:
    yield mindmap_chunks
  else:
    all_chunks = []
    for chunk in iter:
      if chunk == "<|im_end|>": break
      all_chunks.append(chunk)
      yield chunk
    callable(''.join(all_chunks))

def tmp(x):
  global mindmap_chunks
  mindmap_chunks = x

@app.get('/get_mindmap')
def read_minmap_md(url: str) -> str:
  if not url.endswith('.pdf'): url += '.pdf'
  paper = utils.get_paper(url)
  if paper is None: raise HTTPException(status_code=500, detail='Couldn\'t find paper in DB')
  print('Mindmap in DB:', paper.mindmap)
  if paper.mindmap is None:
    mindmap = utils.generate_mindmap(paper)
    if mindmap is None: raise HTTPException(status_code=500, detail='Couldn\'t generate mindmap of the paper')
    db_utils.save_mindmap(mindmap, url)
    return mindmap

  return paper.mindmap

class CodeReqIn(BaseModel):
  paper_url: str
  mindmap: str

# TODO (rohan): solve for <plan> ... </plan> in the code streaming. Use a var to track, if is_planning
@app.post('/get_code')
def generate_code(inp: CodeReqIn):
  if not inp.paper_url.endswith('.pdf'): inp.paper_url += '.pdf'
  paper = utils.get_paper(inp.paper_url)
  if paper.code is None:
    code = utils.generate_code(inp.mindmap)
    if code is None: raise HTTPException(status_code=500, detail='Couldn\'t generate code for the paper')
    db_utils.save_code(code, str(inp.paper_url))
    return code
  return paper.code


if __name__ == '__main__':
  import uvicorn
  uvicorn.run('api:app', host='localhost', port=8080, reload=True)
