import { useEffect, useState, useRef } from 'react'
import { getCode, getDummyCode } from '@/api'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { solarizedlight } from 'react-syntax-highlighter/dist/esm/styles/prism';



const CodeTab = (props) => {
  const [code, setCode] = useState('')

  const updateCode = (newCode) => {
    setCode(prevCode => {
      return `${prevCode}${newCode}`
    })
  }

  useEffect(() => {
    getCode(props.mindmap, props.url).then(res => setCode(res));

    /*
    const iterator = getCode(props.mindmap)
    let processNext = () => {
      iterator.next().then(({ value, done }) => {
        if (done) {
          return;
        }
        console.log(value)
        updateCode(value);
        processNext();
      }).catch(error => {
        console.error('Error:', error);
      });
    }
    processNext();
    */

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
