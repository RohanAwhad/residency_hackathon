from fastapi import FastAPI
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

@app.get('/get_mindmap')
def read_minmap_md(url: str):
  paper = utils.get_paper(url)
  mindmap_iter = utils.generate_mindmap(paper)
  mindmap = []
  for chunk in mindmap_iter:
    if chunk == 0: break
    mindmap.append(chunk)
    # stream the mindmap to the client
    print(chunk)
    print('-'*80)
    yield StreamOut(chunk=chunk, is_done=False)
  
  # signal that the mindmap generation is done
  yield StreamOut(chunk=''.join(mindmap), is_done=True)
  

class CodeReqIn(BaseModel):
  mindmap: str

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