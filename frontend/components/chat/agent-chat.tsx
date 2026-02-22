'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Send, Loader2, MessageSquarePlus, History } from 'lucide-react';
import { sendChatMessage, ChatMessage, getChatSessions, getSessionMessages, ChatSession } from '@/lib/api';
import { MarkdownMessage } from './markdown-message';

export function AgentChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<number | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [showSidebar, setShowSidebar] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const loadSessions = async () => {
    try {
      const data = await getChatSessions();
      setSessions(data);
    } catch (e) {
      console.error('Failed to load sessions:', e);
    }
  };

  const loadSession = async (id: number) => {
    try {
      const msgs = await getSessionMessages(id);
      setMessages(msgs);
      setSessionId(id);
      setShowSidebar(false);
    } catch (e) {
      console.error('Failed to load session:', e);
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setSessionId(undefined);
    setShowSidebar(false);
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      sender: 'user',
      text: input,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage(input, sessionId);
      setSessionId(response.session_id);
      setMessages(prev => [...prev, response.agent_response]);
      loadSessions();
    } catch (e: any) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'agent',
        text: `Sorry, I encountered an error. Please try again. ${e.message || ''}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full bg-card rounded-lg border border-border overflow-hidden">
      {/* Sessions Sidebar */}
      {showSidebar && (
        <div className="w-64 border-r border-border bg-secondary flex flex-col">
          <div className="p-4 border-b border-border">
            <h3 className="font-semibold text-foreground">Chat History</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {sessions.map(session => (
              <button
                key={session.id}
                onClick={() => loadSession(session.id)}
                className={`w-full text-left p-3 rounded-lg mb-2 hover:bg-background transition-colors ${
                  sessionId === session.id ? 'bg-background' : ''
                }`}
              >
                <p className="text-sm font-medium text-foreground truncate">{session.title}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {new Date(session.created_at).toLocaleDateString()}
                </p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Chat */}
      <div className="flex flex-col flex-1">
        {/* Chat Header */}
        <div className="border-b border-border p-4 bg-secondary flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-foreground">Matrax Tyres AI Assistant 🚗</h3>
            <p className="text-sm text-muted-foreground">Your friendly tyre specialist</p>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={() => setShowSidebar(!showSidebar)}
              variant="outline"
              size="sm"
            >
              <History className="w-4 h-4" />
            </Button>
            <Button
              onClick={startNewChat}
              variant="outline"
              size="sm"
            >
              <MessageSquarePlus className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Messages */}
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-6 space-y-4 bg-background"
        >
          {messages.length === 0 && (
            <div className="text-center text-muted-foreground py-12">
              <p className="text-lg font-medium">👋 Welcome to Matrax Tyres!</p>
              <p className="text-sm mt-2">Tell me about your car and I'll help you find the perfect tyres.</p>
              <p className="text-xs mt-4 text-muted-foreground">Try: "I have an Audi A4"</p>
            </div>
          )}
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-2xl px-4 py-3 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-foreground border border-border'
                }`}
              >
                {message.sender === 'agent' ? (
                  <MarkdownMessage text={message.text} sender={message.sender} />
                ) : (
                  <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                )}
                <p className={`text-xs mt-2 ${
                  message.sender === 'user'
                    ? 'text-primary-foreground opacity-70'
                    : 'text-muted-foreground'
                }`}>
                  {message.timestamp}
                </p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-secondary text-foreground border border-border px-4 py-3 rounded-lg flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Thinking...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-border p-4 bg-card">
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="Type your message... e.g., I have an Audi A4"
              className="flex-1 px-4 py-2 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={loading}
            />
            <Button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
