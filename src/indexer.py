import numpy as np
from src.encoder import EncoderModel
import json
import os

model_name = 'bert-base-uncased'
model = EncoderModel(model_name)

def create_index(paper_dict):
    print('creating index')
    all_paragraphs = []
    for key, paper_dict in paper_dict.items():
        index_path = paper_dict['save_path'].split('\\')[0]
        if not os.path.exists(os.path.join(index_path, 'encodings.npy')):

            print(index_path)
            parsed_paper = paper_dict['parsed_pdf']
            parsed_references = paper_dict['parsed_references']

            for section in parsed_paper['sections']:
                all_paragraphs.append(section['text'])

            for ref_id, parsed_reference in parsed_references.items():
                for section in parsed_reference['parsed_paper']['sections']:
                    all_paragraphs.append(section['text'])

            id2para = {i: para for i, para in enumerate(all_paragraphs)}
            text_list = all_paragraphs
            embeddings = model.encode_text(text_list)
            np.save(os.path.join(index_path, 'encodings.npy'), embeddings)
            with open(os.path.join(index_path, 'id2para_map.json'), 'w') as f:
                json.dump(id2para, f)
