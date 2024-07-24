from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

class StreamOut(BaseModel):
  chunk: str
  is_done: bool

def stream_response(iter):
  for chunk in iter:
    print(chunk)
    yield chunk

@app.get('/get_mindmap')
def read_minmap_md(url: str):
  paper = utils.get_paper(url)
  mindmap_iter = utils.generate_mindmap(paper)
  return StreamingResponse(mindmap_iter, media_type='text/plain')

class CodeReqIn(BaseModel):
  mindmap: str

# TODO (rohan): figure this one out too!
@app.post('/get_code')
def generate_code(inp: CodeReqIn):
  code_iter = utils.generate_code(inp.mindmap)
  code = []
  for chunk in code_iter:
    if chunk == 0: break
    code.append(chunk)
    # stream the code to the client
    print(chunk)
    print('-'*80)
    yield StreamOut(chunk=chunk, is_done=False)

  yield StreamOut(chunk=''.join(code), is_done=True)


if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, host='localhost', port=8080)