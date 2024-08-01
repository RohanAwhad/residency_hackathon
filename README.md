### TODOs:

- [ ] Streaming for chat
- [ ] Polling for references till all are loaded
- [ ] Insert docs into database

### Current Flow of Backend:

1. Paper URL comes in
2. Download the paper from the url
3. SciPDF Parse it
4. Save in Postgres
  - What if I return the reference ids for papers?
  - Now there can be multiple request for each (paper_url, reference_id) pair, which would allow me to, one run them in async triggered from client and two make it modular, and not worry about timeout.
5. Get reference ids and for each id
  1. Download reference paper
  2. Use reference context and reference paper to answer 3 questions. (TODO: Handle long papers)
  3. Save to postgres
6. <TO-ADD />


### Updated flow

for now let's implement the above, as soon as we get the paper url
1. POST /process?url=https://arxiv.org/pdf/some.research.pdf
  - This should do all the steps from 1 till 5.3
  - __Is this slow?__: __NOT AT ALL__ I can download and parse a pdf in less than 10 secs on average
  - But this should be async. I mean, this process will take a long time to run. So, after getting the paper url, I need to add it to some queue, and then return 200
  - Can I use PostGres as Queue?
    - What can you not do with PG! LISTEN/NOTIFY can help me build MSG Queue!
    - So, I can create multiple tables that would act as intermediate queues. But first would be to process current paper
    - Any new row added here would trigger a notification to a channel, and python would be listening to that channel, so it will get on it ASAP.
  - Should I just go with threading? At the end of the day, its mostly that only.
    - I can use a dict { paper_url: thread }
2. Given a paper_url and reference_id, search, download, parse and do QA for 3 questions on the reference paper


### Prompts

##### For Citation Info

### Paper Title

Paper Text

### Section Heading

Section Text

### Reference to focus on 


