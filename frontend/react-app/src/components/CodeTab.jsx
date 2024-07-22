import { useEffect, useState, useRef } from 'react'
import { generateCode, getDummyCode } from '@/api'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { solarizedlight } from 'react-syntax-highlighter/dist/esm/styles/prism';



const CodeTab = (props) => {
  const [code, setCode] = useState('')

  useEffect(() => {
    generateCode(props.mindmap).then(code => {
      setCode(code)
    })

    // setCode(getDummyCode())
  }, [])

  let ret;
  if (code) {
    ret = (
      <SyntaxHighlighter language="python" style={solarizedlight}>
        {code}
      </SyntaxHighlighter>
    )
  } else {
    ret = "Generating Code ..."
  }

  return (
    ret
  )
}

export default CodeTab