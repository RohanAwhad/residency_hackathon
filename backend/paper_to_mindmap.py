import google.generativeai as genai
import io
import os
import requests
import functools

from PyPDF2 import PdfReader

GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
# Configure the API key
genai.configure(api_key=GEMINI_API_KEY)

# Specify the Gemini-Flash model
gemini_flash = "gemini-1.5-flash"
gemini_pro = "gemini-1.5-pro"

# Function to generate text
@functools.lru_cache(maxsize=128)
def generate_mindmap(paper):
  """Generates text using Gemini-Flash

  Args:
      prompt: The text prompt for generation.

  Returns:
      The generated text as a string.
  """
  model = genai.GenerativeModel(gemini_flash)
  with open('paper_to_mindmap_prompt.txt', 'r') as f: sys_prompt = f.read()
  response = model.generate_content([sys_prompt, paper])
  return response.text

@functools.lru_cache(maxsize=128)
def find_gaps_in_research(paper):
  model = genai.GenerativeModel(gemini_pro)
  with open('research_gaps_prompt.txt', 'r') as f: sys_prompt = f.read()
  response = model.generate_content([sys_prompt, paper])
  return response.text

@functools.lru_cache(maxsize=128)
def generate_code(mindmap):
  model = genai.GenerativeModel(gemini_pro)
  with open('paper_to_python_prompt.txt', 'r') as f: sys_prompt = f.read()
  response = model.generate_content([sys_prompt, mindmap])
  # extract code enclosed in "```python" &  "```"
  code = response.text.split("```python")[1].split("```")[0]
  return code.strip()

@functools.lru_cache(maxsize=128)
def get_paper_text(url):
  # Step 1: Download the PDF from a given URL
  response = requests.get(url)
  response.raise_for_status()  # Ensure the request was successful

  # Step 2: Store the PDF in an IO buffer
  pdf_buffer = io.BytesIO(response.content)

  # Step 3: Read the contents using PyPDF
  pdf_reader = PdfReader(pdf_buffer)
  text = ""

  # Extract text from each page
  for page in pdf_reader.pages:
    text += page.extract_text() + "\n"
  return text

def main(url):
  text = get_paper_text(url)
  mindmap = generate_mindmap(text)
  return mindmap



# ===
# Utils
# ===
def save_text(text, filename):
  with open(filename, 'w') as f: f.write(text)

def load_text(filename):
  with open(filename, 'r') as f: return f.read()


if __name__ == '__main__':
  url = 'https://arxiv.org/pdf/2308.09729.pdf'  # Example URL
  text = get_paper_text(url)
  save_text(text, 'paper_text.txt')
  text = load_text('paper_text.txt')
  print('Text extracted from the PDF')
  mindmap = generate_mindmap(text)
  save_text(mindmap, 'mindmap.txt')
  print(mindmap)
  # gaps = find_gaps_in_research(text)
  # save_text(gaps, 'gaps.txt')
  # print(gaps)
  code = generate_code(load_text('mindmap.txt'))
  save_text(code, 'code.txt')
  print(code)
  # extract