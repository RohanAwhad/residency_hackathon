import os

PAPERS_DIR = './data/papers/'
BRAVE_SEARCH_API_KEY = os.getenv('BRAVE_SEARCH_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

print(BRAVE_SEARCH_API_KEY)
print(GEMINI_KEY)