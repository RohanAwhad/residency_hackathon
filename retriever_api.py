import os
import faiss
import json
import numpy as np
from src.encoder import EncoderModel
from fastapi import FastAPI
import uvicorn
from src.indexer import create_index
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app = FastAPI()
paper_dict_path = './data/paper_metadata.json'

if os.path.exists(paper_dict_path):
    paper_dict = json.load(open(paper_dict_path, 'r'))
    print('Creating index')
    create_index(paper_dict)

# Initialize the index

# Initialize the encoder
model = EncoderModel('bert-base-uncased')

@app.post("/retrieve")
def retrieve_from_index(request: dict):
    index = faiss.IndexFlatIP(768)
    """Retrieve paragraphs from the index"""
    paper_path = request['save_path'].split('\\')[0]
    print(paper_path)
    with open(os.path.join(paper_path, 'id2para_map.json'), 'r') as f:
        id2para_map = json.load(f)

    # Load the encodings into the index
    encodings = np.load(os.path.join(paper_path, 'encodings.npy'))
    index.add(encodings)
    paragraphs = index.search(model.encode_text([request['query']]).astype(np.float32), 5)
    context = ""
    for pid in paragraphs[1][0]:
        context += id2para_map[f"{pid}"] + "\n"
    return {'context': context}


if __name__ == '__main__':
    uvicorn.run("retriever_api:app", host='0.0.0.0', port=8002, workers=1)
