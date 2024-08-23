Welcome to Explore Your Research paper extension.

We built this extension, to easily go through research paper and their references without breaking the flow. That also got us to thinking of all the things we usually do with the research paper, and so we implemented those features in it.

Current Features:
  1. Information about the References
  2. Chat with your paper and its references
  3. Get a mindmap of the current paper
  4. Get starter code of the current paper to quickly get started with the implementation

### How to Run:

0. Prerequistes:
  - Conda
  - Docker

1. Clone this repo:
  ```bash
  git clone https://github.com/rohanawhad/residency_hackathon
  ```

2. Source `.local.env`. You can update the values as you see fit there. You need to add your Brave Search and Together AI API Key.
  ```bash
  # .local.env
  export PG_USER=residency
  export PG_PASSWORD= # provide a password for PostgreSQL
  export PG_HOST=localhost
  export PG_PORT=5433
  export PG_DB=pdf_extension
  export EMBEDDING_MODEL_DIR="avsolatorio/NoInstruct-small-Embedding-v0"
  export JWT_SECRET= # provide a secret for API signing
  export BRAVE_SEARCH_API_KEY=  # get this from Brave Search API
  export TOGETHER_API_KEY=  # go to Together AI
  ```
  ```bash
  source .local.env
  ```

3. Create and activate python env for backend
  ```bash
  conda env create -f backend/env.yaml
  conda activate pdf_extension_env
  ```

4. Move to backend dir
  ```bash
  cd backend
  ```

5. Start docker containers by upping the docker compose
  ```bash
  docker-compose up -d
  ```

6. Create tables in DB.
  ```bash
  python db_utils.py
  ```

7. Now, start the python API
  ```bash
  python api.py
  ```

8. Finally, we can install the extension. To do this, follow the steps below:
  1. Open "Google Chrome"
  2. Go to "Manage Extensions"
  3. Click on "Load Unpacked"
  4. Browse and select the folder with "<path to repo>/frontend/extension"

Voila! You now have the extension. Go to any Arxiv PDF or any other research paper and test it out.

Let us know your feedback! 
