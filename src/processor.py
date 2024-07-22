import os
from src.scraper import download_from_url, download_from_title, save_pdf
from src.pdf_parser import parse_pdf, extract_references
from tqdm import tqdm
from src.prompting.prompts import summary_generator_prompt, qa_prompt, parse_qa
import requests
import time


def download_all_references(references, base_paper=None):
    parsed_references = {}

    for i, title in tqdm(enumerate(references), total=len(references)):
        ref_id = i + 1
        time.sleep(1)
        if title != '':
            file_path, paper_url = download_from_title(title, is_reference=True, base_paper=base_paper)
            if file_path is None:
                pass
            else:
                try:
                    parsed_paper = parse_pdf(file_path, is_reference=True, base_paper=base_paper)
                    parsed_references[ref_id] = {'parsed_paper': parsed_paper, 'url': paper_url}
                except:
                    pass
    return parsed_references


def get_paper_summary(parsed_pdf):
    paper_data = [section['heading'] + '\n' + section['text'] for section in parsed_pdf['sections']]
    input_prompt = summary_generator_prompt.format(research_paper=paper_data)
    summary = requests.post('http://localhost:8001/get_response', json={'input_prompt': input_prompt}).json()
    return summary


def process(paper_dict, url):
    file_path = paper_dict[url]['save_path']
    print('file_path', file_path)
    paper_dir = '/'.join(file_path.split('\\')[:-1])

    if 'parsed_pdf' not in paper_dict[url]:
        parsed_pdf = parse_pdf(file_path)
        paper_dict[url]['parsed_pdf'] = parsed_pdf

    if 'references' not in paper_dict[url]:
        references = extract_references(paper_dict[url]['save_path'])
        print('references', references)
        paper_dict[url]['references'] = references

    if not os.path.exists(os.path.join(paper_dir, 'references')):
        os.makedirs(os.path.join(paper_dir, 'references'))

    if 'parsed_references' not in paper_dict[url]:
        parsed_references = download_all_references(paper_dict[url]['references'],
                                                    file_path.split('\\')[-1].replace('.pdf', ''))
        paper_dict[url]['parsed_references'] = parsed_references

    if 'summary' not in paper_dict[url]:
        paper_dict[url]['summary'] = get_paper_summary(paper_dict[url]['parsed_pdf'])

    if 'qa_for_references' not in paper_dict[url]:
        qa_for_references = get_qa_for_refs(paper_dict[url]['references'],
                                            paper_dict[url]['parsed_references'])

        paper_dict[url]['qa_for_references'] = qa_for_references
    return paper_dict


def get_qa_for_refs(references, parsed_references):
    qa_for_references = {}
    for section_title, section in tqdm(references.items(), desc=f'Getting QA for sections',
                                       total=len(references.items())):
        if section_title not in qa_for_references:
            qa_for_references[section_title] = {}
        section_references = section['references']
        for ref_id in tqdm(section_references, desc=f'Getting QA for references', total=len(section_references)):
            if ref_id in parsed_references:
                ref_dict = parsed_references[ref_id]['parsed_paper']
                if ref_id not in qa_for_references[section_title]:
                    qa_for_references[section_title][ref_id] = {}
                    input_prompt = qa_prompt(ref_dict, section_title, section['section_text'])
                    answer = requests.post('http://localhost:8001/get_response',
                                           json={'input_prompt': input_prompt}).json()['response']
                    qa_for_references[section_title][ref_id]['qa_pairs'] = parse_qa(answer)
                    qa_for_references[section_title][ref_id]['paper_data'] = {'title': ref_dict['title'],
                                                                              'first_author':
                                                                                  ref_dict['authors'].split(';')[0],
                                                                              'url': parsed_references[ref_id][
                                                                                  'url']}
    return qa_for_references
