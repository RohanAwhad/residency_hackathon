import os
import requests
from src.config import PAPERS_DIR, BRAVE_SEARCH_API_KEY


def brave_search(query, count=5, api_key=BRAVE_SEARCH_API_KEY):
    base_url = "https://api.search.brave.com/res/v1/web/search"

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
    }

    if api_key:
        headers["X-Subscription-Token"] = api_key

    params = {
        "q": query,
        "count": min(count, 20),  # Brave Search API allows max 20 results per request
    }

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()
        paper_url = None
        for result in data.get("web", {}).get("results", []):
            if "arxiv.org" in result["url"]:
                paper_url = result["url"].replace("https://arxiv.org/abs/", "https://arxiv.org/pdf/")
                break
            if result["url"].endswith(".pdf"):
                paper_url = result["url"]
                break
        return paper_url
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def search_paper(title):
    paper_url = brave_search(title)
    return paper_url


def save_pdf(content, paper_url, is_reference=False, base_paper=None):
    if base_paper is None:
        if not os.path.exists(os.path.join(PAPERS_DIR, paper_url.split('/')[-1])):
            os.makedirs(os.path.join(PAPERS_DIR, paper_url.split('/')[-1]))
    file_path = os.path.join(PAPERS_DIR, paper_url.split('/')[-1], paper_url.split('/')[-1] + '.pdf', )
    if is_reference:
        file_path = os.path.join(PAPERS_DIR, base_paper, 'references',
                                 paper_url.split('/')[-1] + '.pdf', )
    print('saved to', file_path)
    with open(file_path, 'wb') as file:
        file.write(content)
    return file_path


def download_from_url(url):
    try:
        pdf_response = requests.get(url).content
        # print(pdf_response)
        # save_path = save_pdf(pdf_response.content, url, is_reference=is_reference, base_paper=base_paper)
        return pdf_response
    except Exception as e:
        print(e)
        print("Paper not found")
        return None


def download_from_title(title):
    try:
        paper_url = search_paper(title)
        if paper_url is not None:
            pdf_response = requests.get(paper_url).content
            # save_path = save_pdf(pdf_response.content, paper_url, is_reference=is_reference,
            #                      base_paper=base_paper)
            return pdf_response, paper_url
        else:
            print("Paper not found")
            return None, None
    except Exception as e:
        print(e)
        print("Paper not found")
        return None, None