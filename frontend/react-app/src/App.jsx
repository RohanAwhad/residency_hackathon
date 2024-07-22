import './App.css'
import CitationTab from '@/components/CitationTab'
import ChatTab from './components/ChatTab'
import GraphTab from './components/GraphTab'
import CodeTab from './components/CodeTab'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useEffect, useState } from 'react'

function App() {
  const [url, setUrl] = useState(undefined)
  const [mindmap, setMindmap] = useState(undefined)

  useEffect(() => {
    function handleStorageChange () {
      console.log('storage change')
      setUrl(localStorage.getItem('currentUrl'))
    }

    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [])

  // useEffect(() => {
  //   setUrl("https://arxiv.org/pdf/2006.15720")
  // }, [])

  let codeTab;
  if (mindmap) { codeTab = <CodeTab mindmap={mindmap} /> }
  else { codeTab = "Generating ..." }

  return (
    <>
      {/* {url && <h1 className="text-2xl font-bold text-center">{url}</h1>} */}
      <Tabs defaultValue="citations" className="w-full h-screen">
        <TabsList className="grid w-full grid-cols-4 h-fit">
          <TabsTrigger value="citations" className="text-base font-medium">References</TabsTrigger>
          <TabsTrigger value="chat" className="text-base font-medium">Chat</TabsTrigger>
          <TabsTrigger value="graph" className="text-base font-medium">Graph</TabsTrigger>
          <TabsTrigger value="code" className="text-base font-medium">Code</TabsTrigger>
        </TabsList>
        <TabsContent value="citations"><CitationTab url={url}/></TabsContent>
        <TabsContent value="chat"><ChatTab url={url}/></TabsContent>
        <TabsContent value="graph"><GraphTab url={url} setMindmap={setMindmap} mindmap={mindmap}/></TabsContent>
        <TabsContent value="code">
          <CodeTab mindmap={mindmap} />
        </TabsContent>
      </Tabs>
    </>
  )
}

export default App
