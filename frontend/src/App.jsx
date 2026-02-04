import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { Bot, Send, Terminal, FileText, Activity, User, AlertCircle } from 'lucide-react'

// Simple utility to generate session IDs (Thread IDs)
const generateThreadId = () => 'session_' + Math.random().toString(36).substr(2, 9);
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello, I am TITAN. I can analyze financial reports, calculate ratios, and fetch real-time market data. Ask me to analyze a company (e.g., Apple).' }
  ])
  const [reportHtml, setReportHtml] = useState(null)
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [threadId, setThreadId] = useState('')

  // Reference for chat auto-scroll
  const chatEndRef = useRef(null)

  // At startup, we generate a unique Thread ID for this session.
  useEffect(() => {
    const storedId = sessionStorage.getItem('titan_thread_id') || generateThreadId();
    sessionStorage.setItem('titan_thread_id', storedId);
    setThreadId(storedId);
  }, []);

  // Auto-scroll when receiving messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userQuestion = input;
    setInput(''); // Clean input

    // Add message from user to the chat
    setMessages(prev => [...prev, { role: 'user', content: userQuestion }]);
    setIsLoading(true);

    try {
      // Call to the API (Backend)
      const response = await axios.post(`${API_URL}/chat/agent`, {
        question: userQuestion,
        thread_id: threadId
      });

      const data = response.data;

      if (data.status === "PAUSED") {
        // case HITL (Human In The Loop)
        setMessages(prev => [...prev, {
          role: 'ai',
          content: `System Paused: ${data.message} Error: ${data.error}. Please check the console logs or use the resume endpoint.`
        }]);
      } else {
        // Process Successful Response
        // If the response looks like HTML, we send it to the right viewer
        if (data.answer && (data.answer.trim().startsWith("<!DOCTYPE html>") || data.answer.trim().startsWith("<div"))) {
          setReportHtml(data.answer);
          setMessages(prev => [...prev, {
            role: 'ai',
            content: 'Analysis Complete. I have generated the strategic report in the dashboard panel.'
          }]);
        } else {
          // If it's normal text (e.g., quick reply), it goes to the chat.
          setMessages(prev => [...prev, { role: 'ai', content: data.answer }]);
        }
      }

    } catch (error) {
      console.error("API Error:", error);
      setMessages(prev => [...prev, {
        role: 'ai',
        content: 'Connection Error. Please ensure the TITAN backend is running.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-screen overflow-hidden font-sans text-slate-200 bg-slate-950">

      {/* LEFT PANEL: Chat Interface (30%) */}
      <div className="w-[400px] flex-shrink-0 flex flex-col border-r border-white/10 bg-slate-900/50 backdrop-blur-sm relative z-10">

        {/* Header */}
        <div className="h-20 flex items-center px-6 border-b border-white/10 glass">
          <div className="w-10 h-10 bg-blue-600/20 border border-blue-500/30 rounded-xl flex items-center justify-center mr-3 shadow-glow">
            <Bot className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h1 className="font-bold text-slate-100 tracking-tight text-lg">TITAN <span className="text-blue-500">CONSOLE</span></h1>
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">System Online</span>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth custom-scrollbar">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'} gap-3`}>

                {/* Avatar Icon */}
                <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${msg.role === 'user' ? 'bg-blue-600' : 'bg-slate-700'
                  }`}>
                  {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                </div>

                {/* Message Bubble */}
                <div className={`p-4 rounded-2xl text-sm leading-relaxed shadow-md ${msg.role === 'user'
                    ? 'bg-blue-600/90 text-white rounded-tr-none'
                    : 'bg-slate-800/80 text-slate-300 rounded-tl-none border border-white/5'
                  }`}>
                  {msg.content}
                </div>
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex justify-start w-full">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center animate-pulse">
                  <Activity size={14} className="text-blue-400" />
                </div>
                <div className="bg-slate-800/50 rounded-2xl p-4 flex items-center space-x-1.5 border border-white/5">
                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-5 border-t border-white/10 bg-slate-900/90">
          <div className="relative group">
            <input
              type="text"
              placeholder="Command the agent (e.g., 'Analyze Apple')..."
              className="w-full bg-slate-950 text-slate-200 border border-slate-700/50 rounded-xl py-4 pl-5 pr-14 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 transition-all placeholder:text-slate-600 shadow-inner"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="absolute right-2 top-2 bottom-2 p-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 text-white rounded-lg transition-all duration-200 shadow-lg shadow-blue-600/20 flex items-center justify-center w-10"
            >
              {isLoading ? <Activity className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </div>
          <div className="mt-3 flex justify-between items-center text-[10px] text-slate-600 px-1">
            <span className="flex items-center gap-1.5"><Terminal size={10} /> Agentic Workflow v1.0</span>
            <span className="font-mono opacity-50">Session: {threadId.slice(0, 12)}...</span>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL: Report Viewer (70%) */}
      <div className="flex-1 flex flex-col bg-slate-950 relative overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
          <div className="absolute -top-[20%] -right-[10%] w-[50%] h-[50%] bg-blue-600/10 rounded-full blur-[120px]"></div>
          <div className="absolute top-[40%] left-[10%] w-[30%] h-[30%] bg-emerald-500/5 rounded-full blur-[100px]"></div>
        </div>

        {/* Report Container */}
        {reportHtml ? (
          <div className="flex-1 overflow-auto p-8 relative z-10 animate-fade-in">
            <div
              className="w-full max-w-6xl mx-auto shadow-2xl rounded-xl overflow-hidden ring-1 ring-white/10"
              dangerouslySetInnerHTML={{ __html: reportHtml }}
            />
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-12 relative z-10 opacity-50">
            <div className="p-8 rounded-full bg-slate-900/50 border border-white/5 mb-6 animate-pulse-slow">
              <FileText className="w-16 h-16 text-slate-700" />
            </div>
            <h3 className="text-slate-300 text-xl font-medium mb-2 tracking-wide">Awaiting Analysis</h3>
            <p className="text-slate-500 text-sm max-w-sm text-center leading-relaxed">
              Select a target company and initiate an audit. TITAN will generate a comprehensive strategic report here.
            </p>
          </div>
        )}
      </div>

    </div>
  )
}

export default App