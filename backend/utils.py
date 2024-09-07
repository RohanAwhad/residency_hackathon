import asyncio
import google.generativeai as genai
import json
import os
import re
import requests
import functools

from pydantic import BaseModel
from typing import Optional

import data_models
import db_utils

# ===
# Constants
# ===
PROMPT_DIR = "prompts"

# ===
# Functions
# ===
import dataclasses
import tempfile
import requests
import scipdf


@dataclasses.dataclass
class ProcessCurrPaperOut:
    url: str
    ref_ids: list[str]


def _get_section_text(sections):
    return "\n\n".join(
        [f"### {sec['heading'].strip()}\n\n{sec['text'].strip()}\n" for sec in sections]
    )


async def parse_with_scipdf(fn: str) -> dict:
    # before sending a request check if server is alive
    try:
        res = requests.get(f'http://{os.environ["GROBID_SERVER_IP"]}:8070/api/isalive')
        if res.status_code != 200 or res.text != 'true':
            raise Exception('Grobid server is not alive')
    except Exception as e:
        print('Error:', e)
        print('Starting Grobid Server')
        # boto3 script to start server
        import boto3
        instance_name = 'grobid-server'
        region = 'us-east-1'
        ec2 = boto3.client('ec2', aws_access_key_id=os.environ['AWS_ACCESS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'], region_name=region)
        # Find the instance by name
        response = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}])
        # Check if any instances were found
        if not response['Reservations']: print(f"No instance found with name: {instance_name}")
        # Get the instance ID
        instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
        # Start the instance
        try:
            ec2.start_instances(InstanceIds=[instance_id])
            print(f"Successfully started instance {instance_name} (ID: {instance_id})")
        except boto3.exceptions.ClientError as e:
            print(f"Error starting instance: {str(e)}")

    return await asyncio.to_thread(scipdf.parse_pdf_to_dict, fn, grobid_url=f'http://{os.environ["GROBID_SERVER_IP"]}:8070')


async def process_curr_paper(url: str) -> Optional[ProcessCurrPaperOut]:
    if not url.endswith(".pdf"):
        url += ".pdf"

    # check if already_processed
    paper = db_utils.read_paper(url)
    if paper is not None:
        ref_ids = db_utils.get_reference_ids_of_paper(url)
        if ref_ids is not None:
            return ProcessCurrPaperOut(url, ref_ids)
    print("Couldn't find paper in DB, processing it now ...")

    # download pdf
    res = await asyncio.to_thread(requests.get, url)
    if res.status_code != 200:
        print("Failed to download PDF at:", url)
    fn = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(res.content)
        fn = tmp_file.name
    print("PDF downloaded at:", fn)

    # parse pdf
    try:
        pdf_dict = await parse_with_scipdf(fn)
    except Exception as e:
        print(e)
        pdf_dict = None
    finally:
        os.remove(fn)  # delete tmp file post processing

    if pdf_dict is None:
        return None
    paper = data_models.Papers(
        url,
        pdf_dict["title"],
        pdf_dict["authors"],
        pdf_dict["abstract"],
        _get_section_text(pdf_dict["sections"]),
        json.dumps(pdf_dict["sections"]),
    )

    chunks = create_chunks(pdf_dict["abstract"]) if pdf_dict["abstract"] else []
    for sec in pdf_dict["sections"]:
        if sec["text"]:
            chunks.extend(create_chunks(sec["text"]))

    embeddings = None
    if len(chunks) == 0:
        print(f"Chunking Failed for paper with url: {url}!")
    else:
        embeddings = embed(chunks, "sentence")
        if embeddings is None:
            print("Chunk embeddings failed")
        else:
            embeddings = [
                data_models.EmbeddingsIn(paper_url=url, chunk=c, embedding=e)
                for c, e in zip(chunks, embeddings)
            ]

    # parse references
    ref_id_to_sec_heading = {}
    for sec in pdf_dict["sections"]:
        for ref_id in sec["publication_ref"]:
            if ref_id not in ref_id_to_sec_heading:
                ref_id_to_sec_heading[ref_id] = []
            ref_id_to_sec_heading[ref_id].append(sec["heading"].strip())

    references = [
        data_models.References(
            referred_by_paper_url=url,
            reference_id=ref["ref_id"],
            referred_sections=json.dumps(ref_id_to_sec_heading[ref["ref_id"]]),
            title=ref["title"],
            authors=ref["authors"],
            journal=ref["journal"],
            year=ref["year"],
        )
        for ref in pdf_dict["references"]
        if ref["ref_id"] in ref_id_to_sec_heading
    ]

    # I want to have this as a transaction
    if embeddings is None:
        db_utils.insert_paper_n_references(paper, references)
    else:
        db_utils.insert_paper_ref_embeddings(paper, references, embeddings)

    return ProcessCurrPaperOut(url, [ref.reference_id for ref in references])


# create chunks
# TODO: (rohan): remove dependency from langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter


def create_chunks(text: str) -> list[str]:
    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1536,
        chunk_overlap=256,
    )
    return r_splitter.split_text(text)


# Embed chunks
import os
import torch
from transformers import AutoTokenizer, AutoModel


@functools.lru_cache()
def _load_model():
    model_ckpt = os.environ["EMBEDDING_MODEL_DIR"]
    tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
    model = AutoModel.from_pretrained(model_ckpt)
    model.eval()
    return tokenizer, model


EMBEDDING_BATCH_SIZE = 8


@torch.no_grad()
def embed(chunks: list[str], mode: str) -> Optional[list[list[float]]]:
    if not mode in ["sentence", "query"]:
        print('Mode has to either be "sentence" or "query", but got', mode)
        return None

    tokenizer, model = _load_model()
    ret = []
    for i in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch = chunks[i : i + EMBEDDING_BATCH_SIZE]
        inp = tokenizer(batch, return_tensors="pt", padding=True, truncation=True)
        output = model(**inp)

        if mode == "query":
            vectors = output.last_hidden_state * inp["attention_mask"].unsqueeze(2)
            vectors = vectors.sum(dim=1) / inp["attention_mask"].sum(dim=-1).view(-1, 1)
        else:
            vectors = output.last_hidden_state[:, 0, :]

        ret.extend(vectors.numpy().tolist())
    return ret


# chat
def generate_chat_response(
    context: Optional[str], messages: list[data_models.Message], main_paper: str
) -> Optional[str]:

    sys_prompt = f"""You are an helpful assistant who helps user to answer their queries related to a research paper in a conversational style.

    You will be answering the question based on the previous conversation history and the context provided. 
    If the question is not relevant to the conversation history, please answer only based on the context.
    If the question is not relevant to the context and you are unable to answer the question, please just say "I don't know the answer".

    The conversation is based on the following paper, so you can consider it as the main paper. 
    If you need additional context to answer the question, relevant snippets from the referenced papers are provided as context.

    Main Paper:
    {main_paper}"""

    query = messages[-1].content
    modified_msg_prompt = f"### Context\n\n{context}\n\n---\n\nQuery: {query}"
    messages[-1].content = modified_msg_prompt
    messages = [
        data_models.Message("system", sys_prompt),
    ] + messages

    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            messages=[x.__dict__ for x in messages],
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(e)
        return None


# process reference
import openai

client = openai.OpenAI(
    api_key=os.environ["TOGETHER_API_KEY"], base_url="https://api.together.xyz/v1"
)
questions = [
    """How does this reference support the current paper's hypothesis or main argument?
What you should focus on while answering: Understanding the role of the reference in supporting the main points of the research paper is crucial. Does it provide foundational theories, corroborate findings, or offer contrasting views that are addressed within the paper?""",
    """What is the significance of the referenced work in the field, and how current is it?
What you should focus on while answering: Evaluating the relevance and impact of the referenced work helps in understanding its importance. Consider the publication date, the reputation of the authors, and how frequently the work has been cited by other scholars.""",
    """What methodologies or key findings from the referenced work or its related works are relevant to the current study?
What you should focus on while answering : Identifying specific methodologies or findings that are referenced can shed light on the research design, analysis, and conclusions of the current paper. It helps in understanding how the referenced work influences or relates to the study at hand.""",
]
prompt = """
You are a helpful assistant who answers the given questions based on the main paper and the reference paper text.
You are given the important points from the main paper that the user is reading and the important points from a reference paper that is mentioned in the main paper.

You need to understand how the reference is related to the main paper. and answer the following questions. Please answer in a concise manner and only based on the given text.

Your answer needs to be short and to the point.

---

# Reference Paper:

## Title: {}

## Paper

{}

---

# Current Paper

{}

---

Question 1. {}
Question 2. {}
Question 3. {}

Give the output in the following format as json within three backticks (```json{{}}```), only output the following:
{{"Question 1": "<answer_1>", "Question 2": "<answer_2>", "Question 3": "<answer_3>"}}
"""


async def search_brave(query: str, count: int):
    # web search for reference
    brave_search_url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": os.environ["BRAVE_SEARCH_API_KEY"],
    }
    params = {
        "q": query,
        "count": count,  # Brave Search API allows max 20 results per request
    }
    response = await asyncio.to_thread(
        requests.get, brave_search_url, headers=headers, params=params
    )
    if response.status_code != 200:
        print("Brave search api gave non-200 response:", response.status_code)
        return None
    response = response.json()
    if "web" not in response or "results" not in response["web"]:
        print("Brave search didn't return results\n", response)
        return {}
    return response


def get_pdf_url_from_search_results(response):
    for res in response["web"]["results"]:
        res_url = res["url"]
        if "arxiv.org" in res_url:
            return re.sub("arxiv.org/abs", "arxiv.org/pdf", res_url)
        if "aclanthology.org" in res_url:
            if res_url.endswith(".pdf"):
                return res_url
            else:
                if res_url[-1] == "/":
                    return res_url[:-1] + ".pdf"
                return res_url + ".pdf"


async def process_reference(
    paper_url: str, ref_id: str
) -> Optional[data_models.ProcessRefOut]:
    if not paper_url.endswith(".pdf"):
        paper_url += ".pdf"

    # check if already processed
    ret: data_models.ProcessRefOut = db_utils.get_processed_reference(paper_url, ref_id)
    if ret:
        return ret

    # Continue Processing
    info: data_models.RefInfoOut = db_utils.get_reference_info_for_searching(
        paper_url, ref_id
    )

    # search db for reference
    paper = db_utils.search_paper_by_title(info.title.strip().lower())
    if not paper:
        query = f'"{info.title.strip().lower()}"'
        response = await search_brave(query, count=20)
        if response is None:
            return None
        elif len(response) == 0:
            # remove the corresponding reference from the paper if the search result returned nothing
            #db_utils.remove_reference(paper_url, ref_id)
            return data_models.ProcessRefOut("", "", "", "", "", "", deleted=True)
        else:
            ref_url = get_pdf_url_from_search_results(response)
            if not ref_url:
                print("Unable to get paper url from brave search")
                #db_utils.remove_reference(paper_url, ref_id)
                return data_models.ProcessRefOut("", "", "", "", "", "", deleted=True)

        ref_obj = await process_curr_paper(ref_url)
        if not ref_obj:
            print("Error while processing reference paper")
            #db_utils.remove_reference(paper_url, ref_id)
            return data_models.ProcessRefOut("", "", "", "", "", "", deleted=True)

        ref_url = ref_obj.url

    else:
        ref_url = paper.paper_url

    # data for prompt
    ref = db_utils.read_paper(ref_url)
    sections_json = json.loads(db_utils.read_paper(paper_url).sections_json)
    sections_json = {res["heading"]: res["text"] for res in sections_json}
    curr_paper_text = "\n\n".join(
        [
            f"### Section: {h}\n\n{sections_json[h].strip()}\n"
            for h in info.referred_sections
        ]
    )

    messages = [
        dict(
            role="user",
            content=prompt.format(
                ref.title, ref.sections_text, curr_paper_text, *questions
            ),
        )
    ]
    max_iterations = 3
    ans = None
    while max_iterations > 0:
        try:
            res = client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                messages=messages,
                max_tokens=4096,
            )
            content = res.choices[0].message.content
            print(content)
            ptrn = re.compile(r"```json(.*?)```", re.DOTALL)
            ans = json.loads(re.search(ptrn, content).group(1))

            assert "Question 1" in ans
            assert "Question 2" in ans
            assert "Question 3" in ans

            break
        except Exception as e:
            print(e)
            max_iterations -= 1
            ans = None

    # save to postgres
    if ans is None:
        print("LLM messed up")
        return None

    q1 = ans["Question 1"]
    q2 = ans["Question 2"]
    q3 = ans["Question 3"]
    db_utils.insert_reference_info(paper_url, ref_id, ref_url, q1, q2, q3)

    return data_models.ProcessRefOut(
        ref_url,
        info.title,
        info.authors[0] if info.authors else "",
        q1,
        q2,
        q3,
        deleted=False,
    )


class Paper(BaseModel):
    title: str
    abstract: str
    content: str
    mindmap: Optional[str] = None
    code: Optional[str] = None


def get_paper(url: str) -> Optional[Paper]:
    """Get the paper title, abstract and content from a given URL."""

    paper = db_utils.read_paper(url)
    if paper is None:
        return None

    content = []
    for sec in json.loads(paper.sections_json):
        heading = sec["heading"]
        text = sec["text"]
        content.append(f"## {heading}\n{text}")

    return Paper(
        title=paper.title,
        abstract=paper.abstract,
        content="\n\n".join(content),
        mindmap=paper.summary_markdown,
        code=paper.code,
    )


def generate_mindmap(paper: Paper):
    with open(f"{PROMPT_DIR}/paper_to_mindmap_prompt.txt", "r") as f:
        sys_prompt = f.read()
    messages = [
        data_models.Message("system", sys_prompt),
        data_models.Message("user", paper.model_dump_json(indent=2)),
    ]
    max_iters = 3
    while max_iters > 0:
        try:
            res = llm_call(messages)
            ptrn = re.compile(r"```md(.*)```", re.DOTALL)
            return re.search(ptrn, res).group(1).strip()
        except Exception as e:
            print(e)
            max_iters -= 1


def generate_code(mindmap):
    with open(f"{PROMPT_DIR}/paper_to_python_prompt.txt", "r") as f:
        sys_prompt = f.read()
    messages = [
        data_models.Message("system", sys_prompt),
        data_models.Message("user", mindmap),
    ]
    max_iters = 3
    while max_iters > 0:
        try:
            res = llm_call(messages)
            ptrn = re.compile(r"```python(.*)```", re.DOTALL)
            return re.search(ptrn, res).group(1).strip()
        except Exception as e:
            print(e)
            max_iters -= 1


# ===
# Utils
# ===
def llm_call(messages: list[data_models.Message]):
    res = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        messages=[x.__dict__ for x in messages],
        max_tokens=4096,
        temperature=0.8,
    )
    content = res.choices[0].message.content
    return content


def save_text(text, filename):
    with open(filename, "w") as f:
        f.write(text)


def load_text(filename):
    with open(filename, "r") as f:
        return f.read()


if __name__ == "__main__":
    paper = get_paper("https://arxiv.org/abs/2106.04561")
    mindmap_iter = generate_mindmap(paper)
    mindmap = []
    for chunk in mindmap_iter:
        if chunk == 0:
            break
        print(chunk)
        mindmap.append(chunk)
    mindmap = "".join(mindmap)

    code_iter = generate_code(mindmap)
    code = []
    for chunk in code_iter:
        if chunk == 0:
            break
        print(chunk)
        code.append(chunk)
    code = "".join(code)
