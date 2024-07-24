import os
import json
import numpy as np
from src.encoder import EncoderModel

MODEL_NAME = 'bert-base-uncased'
model = EncoderModel(MODEL_NAME)


def create_index(paper_dict):
    print('Creating index')
    for paper_data in paper_dict.values():
        index_path = os.path.dirname(paper_data['save_path'])
        encodings_path = os.path.join(index_path, 'encodings.npy')

        if not os.path.exists(encodings_path):
            print(f'Processing: {index_path}')
            all_paragraphs = get_all_paragraphs(paper_data)

            id2para = {i: para for i, para in enumerate(all_paragraphs)}
            embeddings = model.encode_text(all_paragraphs)

            np.save(encodings_path, embeddings)

            with open(os.path.join(index_path, 'id2para_map.json'), 'w') as f:
                json.dump(id2para, f)


def get_all_paragraphs(paper_data):
    all_paragraphs = []

    # Main paper sections
    for section in paper_data['parsed_pdf']['sections']:
        all_paragraphs.append(section['text'])

    # Referenced papers sections
    for parsed_reference in paper_data['parsed_references'].values():
        for section in parsed_reference['parsed_paper']['sections']:
            all_paragraphs.append(section['text'])

    return all_paragraphs
