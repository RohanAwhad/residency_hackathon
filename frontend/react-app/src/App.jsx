import './App.css'
import CitationCard from '@/components/CitationCard'
import GraphTab from './components/GraphTab'
import CodeTab from './components/CodeTab'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useEffect, useRef, useState } from 'react'

import { getChatResponse, getSummaries, getRefIds, getRefData } from '@/api';
import ChatHistory from '@/components/ChatHistory';
import Suggestions from '@/components/Suggestions';

import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

function App() {
  const [url, setUrl] = useState(undefined)
  const [mindmap, setMindmap] = useState(undefined)
  const [citations, setCitations] = useState([])

  // chat 
  const [messages, setMessages] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [userCurrMsg, setUserCurrMsg] = useState("");
  const [generatingMsg, setGeneratingMsg] = useState(false);
  const scrollRef = useRef(null);

  // ===
  // Utils
  // ===
  useEffect(() => {
    function handleStorageChange () {
      console.log('storage change')
      setUrl(localStorage.getItem('currentUrl'))
    }
    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [])

  /*
  useEffect(() => {
    setUrl("https://arxiv.org/pdf/2006.15720")
  }, [])
  */

  useEffect(() => {
    // pass
    if (!url) return;

    getRefIds(url).then(data => {
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
    //getChatResponse(props.url, [{'role': 'user', 'content': 'What are the nuances of this paper?'}])

  }, url)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleInputChange = (e) => {
    setUserCurrMsg(e.target.value);
  }
  const handleSendMessage = () => {
    console.log("Sending message: ", userCurrMsg);
    let history = messages
    setMessages(messages => {
      const newMessages = [...messages, { is_assistant: false, message: userCurrMsg }]
      return newMessages
    });

    history.push({is_assistant: false, message: userCurrMsg })
    const newHistory = history.map(x => {
      const role = x.is_assistant ? 'assistant' : 'user';
      const content = x.message;
      return {role, content}
    })
    getChatResponse(url, newHistory, userCurrMsg).then((response) => {
      console.log(response);
      setMessages(messages => {
        const newMessages = [...messages, { is_assistant: true, message: response }]
        return newMessages;
      });
      //setSuggestions(response.suggestions);
    });

    setUserCurrMsg("");
    setGeneratingMsg(true);
  }


  return (
    <>
      <Tabs defaultValue="citations" className="w-full h-screen">
        <TabsList className="grid w-full grid-cols-4 h-fit">
          <TabsTrigger value="citations" className="text-base font-medium">References</TabsTrigger>
          <TabsTrigger value="chat" className="text-base font-medium">Chat</TabsTrigger>
          <TabsTrigger value="graph" className="text-base font-medium">Graph</TabsTrigger>
          <TabsTrigger value="code" className="text-base font-medium">Code</TabsTrigger>
        </TabsList>
        <TabsContent value="citations">
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
        </TabsContent>
        <TabsContent value="chat">
          <div className="h-screen grid justify-items-end">
            <ScrollArea className="w-full h-full flex-col" ref={scrollRef}>
              {messages && <ChatHistory messages={messages} />}
              {suggestions && <Suggestions suggestions={suggestions} setUserCurrMsg={setUserCurrMsg} />}
            </ScrollArea>
            <div className="flex rounded-full border-2 items-center w-full px-3 my-3 h-fit">
              <Input className='text-base border-none py-2' type="text" placeholder="Message your Paper" onChange={handleInputChange} value={userCurrMsg} />
              <Button className="text-base my-1 rounded-full w-fit" onClick={handleSendMessage}>
                Send
              </Button>
            </div>
          </div>
        </TabsContent>
        <TabsContent value="graph"><GraphTab url={url} setMindmap={setMindmap} mindmap={mindmap}/></TabsContent>
        <TabsContent value="code">
          <CodeTab mindmap={mindmap} />
        </TabsContent>
      </Tabs>
    </>
  )
}

export default App
