import CitationCard from '@/components/CitationCard'
import { getChatResponse } from '@/api'
import { getSummaries, getRefIds, getRefData } from '@/api'
import { useState, useEffect } from 'react'


export default function CitationTab(props) {
  const [citations, setCitations] = useState([])

  useEffect(() => {
    // pass
    if (!props.url) return;

    getRefIds(props.url).then(data => {
      data.ref_ids.forEach(ref_id => {
        getRefData(data.url, ref_id).then(refData => {
          console.log(refData);
          setCitations(prev => {
            return [...prev,
             {
              id: ref_id.slice(1),
              title: refData.title,
              first_author_name: refData.author,
              why: refData.q1_ans,
              contribution: refData.q2_ans,
              related_works: refData.q3_ans,
            }]
          })
        })
      })
    });

    // TODO (rohan)
    // Remove this
    getChatResponse(props.url, [{'role': 'user', 'content': 'What are the nuances of this paper?'}])


    getSummaries(props.url).then(data => {
      console.log(data)
      setCitations(data)
    })

  }, [])

  return (
    <div>
      {citations && citations.map(data => (
        <CitationCard
          key={data.id}
          id={data.id}
          first_author={data.first_author_name}
          title={data.title}
          why={data.why}
          contribution={data.contribution}
          related_works={data.related_works}
        />
      ))}
    </div>
  )
}
