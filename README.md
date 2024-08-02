Welcome to Explore Your Research paper extension.

We built this extension, to easily go through research paper and their references without breaking the flow. That also got us to thinking of all the things we usually do with the research paper, and so we implemented those features in it.

Current Features:
  1. Information about the References
  2. Chat with your paper and its references
  3. Get a mindmap of the current paper
  4. Get starter code of the current paper to quickly get started with the implementation

### How to Run:

1. Clone this repo:
  ```bash
  git clone https://github.com/rohanawhad/residency_hackathon
  ```

2. Source `.local.env`. You can update the values as you see fit there.
  ```bash
  source .local.env
  ```

3. Create a python env for backend
  ```bash
  conda env create -f backend/env.yaml
  ```

4. Move to backend dir
  ```bash
  cd backend
  ```

5. Create Postgres Container. This instantiation of container, will not delete the container on shut down. This way you can store your DB, unless you manually delete the container.
  ```bash
  bash create_container.sh
  ```

6. Create tables in DB.
  ```bash
  python db_utils.py
  ```

7. Start GROBID server. This will parse our PDF for us. We limit the CPU usage to 4 and RAM to 4GB. This gives the best results in terms of latency
  ```bash
  docker run --rm --init --ulimit core=0 -p 8070:8070 --memory=4096m --cpus=4 lfoppiano/grobid:0.8.0
  ```

8. Now, start the python API
  ```bash
  python api.py
  ```

9. Finally, we can install the extension. To do this, follow the steps below:
  1. Open "Google Chrome"
  2. Go to "Manage Extensions"
  3. Click on "Load Unpacked"
  4. Browse and select the folder with "<path to repo>/frontend/extension"

Voila! You now have the extension. Go to any Arxiv PDF or any other research paper and test it out.

Let us know your feedback! 
