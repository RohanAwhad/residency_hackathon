### TODOs:

- [ ] Streaming for chat
- [ ] Polling for references till all are loaded
- [ ] Insert docs into database

### Current Flow of Backend:

1. Paper URL comes in
2. Download the paper from the url
3. SciPDF Parse it
4. Save in Postgres
5. Get reference ids and for each id
  1. Download reference paper
  2. Use reference context and reference paper to answer 3 questions. (TODO: Handle long papers)
  3. Save to postgres
6. <TO-ADD />


### Updated flow

for now let's implement the above, as soon as we get the paper url
1. POST /process?url=https://arxiv.org/pdf/some.research.pdf
  - This should do all the steps from 1 till 5.3

