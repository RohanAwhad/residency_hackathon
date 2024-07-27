import os
import requests
import scipdf
import tempfile

import db_utils
import db_models
import utils

import time
start = time.monotonic()
url = "https://arxiv.org/pdf/1809.05724"
res = utils.process_curr_paper(url)
print(res)
end = time.monotonic()
print(f'Time Taken to process curr paper: {end - start} secs')
exit(0)
'''

# Download the paper
if not url.endswith('.pdf'): url += '.pdf'
res = requests.get(url)
if res.status_code != 200: print('Failed to download PDF at:', url)
fn = None
with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
  tmp_file.write(res.content)
  fn = tmp_file.name

print('PDF downloaded at:', fn)
end1 = time.monotonic()
print(f'Time taken to download: {end1-start} secs')
'''
#breakpoint()
fn = "/Users/rohan/Downloads/2401.04088.pdf"

# Reasons for reference id not showing up:
#  - Reference id is not being extracted during parse_references: *** NameError: name 'ref_id' is not defined
pdf_dict = scipdf.parse_pdf_to_dict(fn)

import json
with open('parsed_paper_6.json', 'w') as f: json.dump(pdf_dict, f, indent=2)


paper = db_models.Paper(
  fn,
  pdf_dict['title'],
  pdf_dict['authors'],
  pdf_dict['abstract'],
  get_section_text(pdf_dict['sections']),
  json.dumps(pdf_dict['sections'])
)

ref_id_to_sec_heading = {}
for sec in pdf_dict['sections']:
  for ref_id in sec['publication_ref']:
    if ref_id not in ref_id_to_sec_heading: ref_id_to_sec_heading[ref_id] = []
    ref_id_to_sec_heading[ref_id].append(sec['heading'].strip())

references = [
  db_models.References(
    referred_by_paper_url = fn,
    reference_id = ref['ref_id'],
    referred_sections = json.dumps(ref_id_to_sec_heading.get(ref['ref_id'], []))
  )
  for ref in pdf_dict['references']
]

# save to postgres
# return {url: url, ref_ids: [ref_id...]}


# to delete
#os.remove(fn)

end = time.monotonic()
print(f'Time taken to download and parse a paper: {end - start} secs')






# 3. SciPDF Parse it

# 5. Get reference ids and for each id
#  1. Download reference paper
#  2. Use reference context and reference paper to answer 3 questions. (TODO: Handle long papers)
#  3. Save to postgres
