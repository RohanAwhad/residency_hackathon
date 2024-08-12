import './App.css'
import CitationCard from '@/components/CitationCard'
import GraphTab from './components/GraphTab'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useEffect, useRef, useState } from 'react'

import { getChatResponse, getCode, getRefIds, getRefData, getMindmapMd, validateApiKey } from '@/api';
import ChatHistory from '@/components/ChatHistory';
import Suggestions from '@/components/Suggestions';

import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"

import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { solarizedlight } from 'react-syntax-highlighter/dist/esm/styles/prism';

function App() {
  const [apiKey, setApiKey] = useState(undefined)

  const [url, setUrl] = useState(undefined)
  const [citations, setCitations] = useState([])

  // chat 
  const [messages, setMessages] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [userCurrMsg, setUserCurrMsg] = useState("");
  const [generatingMsg, setGeneratingMsg] = useState(false);
  const scrollRef = useRef(null);

  // mindmap
  const [markdown, setMarkdown] = useState('')

  // code
  const [code, setCode] = useState('');
  useEffect(() => {
    if (!url || !markdown || !apiKey) return;
    getCode(markdown, url).then(res => setCode(res));
  }, [url, markdown, apiKey]);

  // ===
  // Utils
  // ===

  useEffect(() => {
    function handleStorageChange() {
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
    if (!url || !apiKey) return;

    // get reference info
    getRefIds(url, apiKey).then(data => {
      data.ref_ids.forEach(ref_id => {
        getRefData(data.url, ref_id).then(refData => {
          if (refData.deleted) { return };
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

    // get mindmap markdown
    getMindmapMd(url).then(md => setMarkdown(md));

  }, [url, apiKey])


  // chat
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleInputChange = (e) => { setUserCurrMsg(e.target.value); }
  const handleKeyDown = e => { if (e.key == 'Enter') { handleSendMessage(); } }

  const handleSendMessage = () => {
    console.log("Sending message: ", userCurrMsg);
    let history = messages
    setMessages(messages => {
      const newMessages = [...messages, { is_assistant: false, message: userCurrMsg }]
      return newMessages
    });

    history.push({ is_assistant: false, message: userCurrMsg })
    const newHistory = history.map(x => {
      const role = x.is_assistant ? 'assistant' : 'user';
      const content = x.message;
      return { role, content }
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

  const apiKeyRef = useRef()
  const errorMsgRef = useRef()
  const handleApiKeySubmission = (e) => {
    e.preventDefault();
    const apiKey = apiKeyRef.current.value;
    validateApiKey(apiKey).then((res) => {
      if (res.isValid) {
        setApiKey(apiKey);
      } else {
        errorMsgRef.current.classList.remove('invisible')
      }
    });
  };

  let ret = <></>
  if (apiKey === undefined) {
    // TODO: (rohan) handle api key request
    ret = (
      <div className="grid grid-cols-1 w-full max-w-lg items-center mx-auto">
        <p className='invisible text-xs mb-2 text-rose-600' ref={errorMsgRef}>Unable to verify API Key</p>
        <Label className='mb-2' htmlFor="api_key">API Key</Label>
        <div className='flex flex-row gap-2 w-xl mb-3'>
          <Input type="password" id="api_key" placeholder="API Key" ref={apiKeyRef} />
          <Button className='rounded-full' onClick={handleApiKeySubmission}>Submit</Button>
        </div>
        <p className="text-gray-500 text-sm mt-2">Please enter your API key to proceed. If you don't have one, kindly visit <a href="https://example.org" className="text-blue-500 hover:text-blue-700">https://example.org</a> to obtain one.</p>
      </div>
    )
  } else {
    ret = (
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
                <Input className='text-base border-none py-2' type="text" placeholder="Message your Paper" onKeyDown={handleKeyDown} onChange={handleInputChange} value={userCurrMsg} />
                <Button className="text-base my-1 rounded-full w-fit" onClick={handleSendMessage}>
                  Send
                </Button>
              </div>
            </div>
          </TabsContent>
          <TabsContent value="graph">
            <GraphTab markdown={markdown} />
          </TabsContent>
          <TabsContent value="code">
            {/*<CodeTab mindmap={markdown} url={url} />*/}
            {code ? (
              <SyntaxHighlighter language="python" style={solarizedlight}>
                {code}
              </SyntaxHighlighter>
            ) : (
              <div>Generating Code</div>
            )}
          </TabsContent>
        </Tabs>
      </>
    )
  }

  return ret
}

export default App
