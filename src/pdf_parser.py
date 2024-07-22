import os
import scipdf
from PyPDF2 import PdfReader
import tempfile


def parse_reference(pdf_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(pdf_content)
        temp_file_path = temp_file.name

    content = ''
    pdf = PdfReader(temp_file_path)
    os.remove(temp_file_path)

    for page in pdf.pages:
        content += page.extract_text()

    return content


def parse_pdf(pdf_file_path, is_reference=False, base_paper=None):
    print(f'Parsing PDF: {pdf_file_path}')
    if is_reference:
        path = os.path.join('data', 'papers', base_paper, 'references', os.path.basename(pdf_file_path))
    else:
        path = pdf_file_path

    path = os.path.abspath(path)
    print(f'Parsing PDF: {path}')
    print(f'File exists: {os.path.exists(path)}')

    article_dict = scipdf.parse_pdf_to_dict(path)
    return article_dict


def get_reference_ids(article_dict):
    reference_ids = []
    for section in article_dict['sections']:
        pub_refs = section['publication_ref']
        for pub_ref in pub_refs:
            if pub_ref not in reference_ids:
                reference_ids.append(pub_ref)
    for ref in article_dict['references']:
        if ref['ref_id'] not in reference_ids:
            reference_ids.append(ref['ref_id'])
    return reference_ids
