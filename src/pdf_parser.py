import os
from PyPDF2 import PdfReader
# import scipdf


def parse_pdf(pdf_file_path, is_reference=False, base_paper=None):
    if is_reference:
        path = os.path.join('./data/papers/', base_paper, 'references', pdf_file_path.split('\\')[-1])
    else:
        path = os.path.join('./data/papers/', pdf_file_path.split('/')[-1])
    path = path.replace('\\', '/')
    print('path', path)
    print(is_reference)
    print(os.path.exists(path))
    pdf_contents = {}
    reader = PdfReader(path)
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        pdf_contents[i + 1] = text
    return pdf_contents


def extract_references(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        num_pages = len(reader.pages)

        references = []
        in_references_section = False
        current_reference = []

        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()

            if 'References' in text or 'REFERENCES' in text:
                in_references_section = True

            if in_references_section:
                lines = text.split('\n')
                for line in lines:
                    if line.strip() == '':
                        continue
                    elif (line.startswith('[') or (line.strip()[0] in [str(i) for i in range(10)]) and len(
                            line) > 100) and current_reference:
                        references.append(''.join(current_reference))
                        current_reference = [line]
                    else:
                        current_reference.append(line)

        if current_reference:
            references.append(''.join(current_reference))

        return references

# def parse_pdf(pdf_file_path, is_reference=False, base_paper=None):
#     if is_reference:
#         path = os.path.join('./data/papers/', base_paper, 'references', pdf_file_path.split('\\')[-1])
#     else:
#         path = os.path.join('../data/papers/', pdf_file_path.split('/')[-1])
#     path = path.replace('\\', '/')
#     print('path', path)
#     path = os.path.abspath(path)
#     print(os.path.exists(path))
#     article_dict = scipdf.parse_pdf_to_dict(path)
#     return article_dict
#
#
# def get_section_wise_references(article_dict):
#     section_wise_references = {}
#     sections = article_dict['sections']
#     for section in sections:
#         section_title = section['heading']
#         section_references = section['publication_ref']
#         section_wise_references[section_title] = {'references': section_references,
#                                                   'section_text': section['text']}
#     return section_wise_references
#
