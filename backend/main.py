from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import paper_to_mindmap

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

@app.get('/mindmap_md')
def read_minmap_md(url: str):
  return paper_to_mindmap.main(url)


class CodeReqIn(BaseModel):
  mindmap: str

class CodeResOut(BaseModel):
  code: str

@app.post('/code')
def generate_code(inp: CodeReqIn):
  ret = CodeResOut(code=paper_to_mindmap.generate_code(inp.mindmap))
  return ret


if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, host='localhost', port=8080)