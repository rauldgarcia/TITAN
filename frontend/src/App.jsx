import { useState } from 'react'
import { Bot, Send, Terminal, FileText, Activity } from 'lucide-react'

function App() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello, I am TITAN. I can analyze financial reports, calculate ratios, and fetch real-time market data. How can I help you today?' }
  ])
  const [reportHtml, setReportHtml] = useState(null)
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden">
      
      {/* LEFT PANEL: Chat Interface (35%) */}
      <div className="w-[400px] flex-shrink-0 flex flex-col border-r border-white/10 bg-slate-900/50 backdrop-blur-sm">
        
        {/* Header */}
        <div className="h-16 flex items-center px-6 border-b border-white/10 glass">
          <Bot className="w-6 h-6 text-blue-500 mr-3" />
          <div>
            <h1 className="font-bold text-slate-100 tracking-tight">TITAN <span className="text-blue-500">CONSOLE</span></h1>
            <div className="flex items-center">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse mr-2"></span>
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">System Online</span>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-br-none shadow-lg shadow-blue-500/20' 
                  : 'bg-slate-800 text-slate-300 rounded-bl-none border border-white/5'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-800 rounded-2xl p-4 flex items-center space-x-2 border border-white/5">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-75"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-150"></div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-white/10 bg-slate-900/80">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Ask TITAN (e.g., 'Analyze Apple's risks')..." 
              className="w-full bg-slate-950 text-slate-200 border border-slate-700 rounded-xl py-3 pl-4 pr-12 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-slate-600"
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button className="absolute right-2 top-2 p-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors">
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="mt-2 text-center">
            <span className="text-[10px] text-slate-600 flex justify-center items-center gap-2">
              <Terminal className="w-3 h-3" /> Powered by LangGraph & MCP
            </span>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL: Report Viewer (65%) */}
      <div className="flex-1 flex flex-col bg-slate-950 relative">
        {/* Background Pattern for Empty State */}
        {!reportHtml && (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-700 opacity-20 pointer-events-none">
            <Activity className="w-32 h-32 mb-4" />
            <h2 className="text-2xl font-bold uppercase tracking-widest">Awaiting Analysis</h2>
          </div>
        )}

        {/* Report Container */}
        {reportHtml ? (
           <div className="flex-1 overflow-auto p-8">
             {/* Aquí inyectaremos el HTML de Jinja2 */}
             <div 
               className="w-full max-w-5xl mx-auto bg-transparent"
               dangerouslySetInnerHTML={{ __html: reportHtml }} 
             />
           </div>
        ) : (
          <div className="flex-1 flex items-center justify-center p-12">
             <div className="glass p-8 rounded-2xl border border-dashed border-slate-700 max-w-lg text-center">
                <FileText className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <h3 className="text-slate-300 font-semibold mb-2">No Report Generated Yet</h3>
                <p className="text-slate-500 text-sm">
                  Start a conversation with TITAN. When the agent generates a strategic report, it will appear here automatically.
                </p>
             </div>
          </div>
        )}
      </div>

    </div>
  )
}

export default App