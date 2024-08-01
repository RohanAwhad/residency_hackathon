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
  return HTTPException(status_code=500, detail="Couldn't process current paper")

# process reference
@app.get('/process_reference')
def process_reference(paper_url: str, ref_id: str):
  ret = utils.process_reference(paper_url, ref_id)
  if ret: return ret
  return HTTPException(status_code=500, detail="Couldn't generate information about this reference")

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
  if query_embeddings is None: return HTTPException(status_code=500, detail='Couldn\'t generate embeddings from user message')
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
def read_minmap_md(url: str):
  paper = utils.get_paper(url)
  mindmap_iter = utils.generate_mindmap(paper)
  # TODO (rohan): add code to save the mindmap in the DB at appropriate location
  return StreamingResponse(stream_response(mindmap_iter, tmp), media_type='text/plain')

class CodeReqIn(BaseModel):
  mindmap: str

# TODO (rohan): solve for <plan> ... </plan> in the code streaming. Use a var to track, if is_planning
@app.post('/get_code')
def generate_code(inp: CodeReqIn):
  code_iter = utils.generate_code(inp.mindmap)
  return StreamingResponse(code_iter, media_type='text/plain')


if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, host='localhost', port=8080)
