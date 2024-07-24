import os
import time
import requests
from tqdm import tqdm
import tempfile
from src.scraper import download_from_title
from src.pdf_parser import parse_pdf, parse_reference, get_reference_ids
from src.prompting.prompts import summary_generator_prompt, qa_prompt, parse_qa
from src.send_to_postgress import main_article_dict_to_postgres, references_data_to_postgres, qa_for_ref_to_postgres
from src.encoder import EncoderModel
from src.ref_data import RefEmbeddings
from src.llm import GeminiModel

# from src.llm import ClaudeModel

encoder = EncoderModel('bert-base-uncased')
llm_model = GeminiModel()


# llm_model = ClaudeModel()


def download_all_references(article_dict, base_paper=None):
    parsed_references = {}
    for ref_dict in tqdm(article_dict['references'], desc="Downloading references"):
        time.sleep(1)
        ref_id = ref_dict['ref_id']
        title = ref_dict['title']
        if title:
            file_path, paper_url = download_from_title(title, is_reference=True, base_paper=base_paper)
            if file_path:
                try:
                    parsed_paper = parse_pdf(file_path, is_reference=True, base_paper=base_paper)
                    parsed_references[ref_id] = {'parsed_paper': parsed_paper, 'url': paper_url}
                except Exception:
                    pass
    return parsed_references


def get_temp_file(pdf_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(pdf_content)
        temp_file_path = temp_file.name
    return temp_file_path


def process(paper_content, url):
    # file_path = paper_dict[url]['save_path']
    # print('file_path', file_path)
    # paper_dir = os.path.dirname(file_path)

    tmp_file_path = get_temp_file(paper_content)

    # if 'parsed_pdf' not in paper_dict[url]:
    parsed_pdf_dict = parse_pdf(tmp_file_path)
    os.remove(tmp_file_path)
    main_article_dict_to_postgres(url, parsed_pdf_dict)

    all_references = get_reference_ids(parsed_pdf_dict)
    results = {}
    ref_id_to_ref = {}
    for ref in parsed_pdf_dict['references']:
        ref_id_to_ref[ref['ref_id']] = ref
    for ref_id in tqdm(all_references, desc="Parsing references"):
        reference = ref_id_to_ref[ref_id]
        title = reference['title']
        ref_id = reference['ref_id']
        authors = reference['authors']
        reference_content, reference_url = download_from_title(title)
        parsed_reference = parse_reference(reference_content)
        qa_for_ref = get_qa_for_refs(parsed_pdf_dict, parsed_reference)
        qa_for_ref_to_postgres(url, ref_id, qa_for_ref, authors)
        results['ref_id'] = {'ref_id': ref_id, 'qa': qa_for_ref, 'authors': authors}
        # reference_chunks = encoder.chunk_text(parsed_reference)
        # embeddings = encoder.encode_text(reference_chunks)
        # reference_data = [RefEmbeddings(ref_id=ref_id, chunk=chunk, embeddings=emb) for chunk, emb in
        #                   zip(reference_chunks, embeddings)]
        #
        # references_data_to_postgres(reference_data)
        break

    return results


def get_qa_for_refs(main_paper, parsed_reference):
    main_paper_content = ''
    main_paper_content += 'Title: ' + main_paper['title'] + '\n' + 'Abstract: ' + main_paper['abstract']
    main_paper_content += '\n'.join([section['heading'] + '\n' + section['text'] for section in main_paper['sections']])
    main_paper_summary = get_paper_summary(main_paper_content)
    ref_paper_summary = get_paper_summary(parsed_reference)
    input_prompt = qa_prompt(main_paper_summary, ref_paper_summary)
    response = llm_model.get_response(input_prompt)
    return response


def get_paper_summary(text):
    input_prompt = summary_generator_prompt.format(research_paper=text)
    response = llm_model.get_response(input_prompt)
    return response['response']
