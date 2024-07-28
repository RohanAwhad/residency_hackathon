from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional

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
