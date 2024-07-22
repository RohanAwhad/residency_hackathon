import CitationCard from '@/components/CitationCard'
import { getDummyData } from '@/api'
import { getSummaries } from '@/api'
import { useState, useEffect } from 'react'


export default function CitationTab(props) {
  const [citations, setCitations] = useState([])

  useEffect(() => {
    // pass
    if (!props.url) return;
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