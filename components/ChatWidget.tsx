"use client"

import { useState, useRef, useEffect } from "react"
import { MessageCircle, Send, X, Minimize2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { CubeIcon } from "@/components/icons/CubeIcon"
import { toast } from "sonner"

interface Message {
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

const initialMessages: Message[] = [
  {
    role: "assistant",
    content: "Hi! I'm Relicon AI. I can help you analyze your ad performance and answer questions about CTR, ROAS, conversions, and more. What would you like to know?",
    timestamp: new Date(),
  },
]

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // TODO: Get user ID from authentication
  const userId = null // Replace with auth.user?.id when auth is implemented

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    if (isOpen && !isMinimized) {
      scrollToBottom()
    }
  }, [messages, isOpen, isMinimized])

  const handleSend = async () => {
    if (!input.trim() || isTyping) return

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsTyping(true)

    try {
      const conversationHistory = messages
        .slice(1)
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }))

      conversationHistory.push({
        role: userMessage.role,
        content: userMessage.content
      })

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: conversationHistory,
          userId: userId
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get response')
      }

      const aiMessage: Message = {
        role: "assistant",
        content: data.message,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, aiMessage])
    } catch (error: any) {
      console.error('Chat error:', error)

      const errorMessage: Message = {
        role: "assistant",
        content: "I apologize, but I encountered an error. Please try again.",
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, errorMessage])
      toast.error('Failed to send message')
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Don't render anything if not on dashboard
  if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/dashboard')) {
    return null
  }

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-white text-black rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-110 flex items-center justify-center group"
          aria-label="Open chat"
        >
          <MessageCircle className="w-6 h-6" />
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
        </button>
      )}

      {/* Chat Widget */}
      {isOpen && (
        <div
          className={`fixed bottom-6 right-6 z-50 bg-[#0d0d0d] border border-[#252525] rounded-2xl shadow-2xl transition-all ${
            isMinimized ? 'w-80 h-16' : 'w-[400px] h-[600px]'
          }`}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-[#252525] bg-[#0a0a0a] rounded-t-2xl">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-[#161616] border border-[#252525] rounded-lg flex items-center justify-center">
                <CubeIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-white text-sm font-semibold">Relicon AI</h3>
                <p className="text-gray-500 text-xs">Analytics Assistant</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-1.5 hover:bg-[#1f1f1f] rounded-lg transition-colors"
                aria-label={isMinimized ? "Expand" : "Minimize"}
              >
                <Minimize2 className="w-4 h-4 text-gray-400" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:bg-[#1f1f1f] rounded-lg transition-colors"
                aria-label="Close chat"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            </div>
          </div>

          {/* Messages Area */}
          {!isMinimized && (
            <>
              <div className="flex-1 overflow-y-auto p-4 space-y-4 h-[calc(600px-180px)]">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex gap-2 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {message.role === "assistant" && (
                      <div className="w-6 h-6 bg-[#161616] border border-[#252525] rounded-md flex items-center justify-center shrink-0">
                        <CubeIcon className="w-4 h-4 text-white" />
                      </div>
                    )}
                    <div
                      className={`max-w-[75%] rounded-lg px-3 py-2 ${
                        message.role === "user"
                          ? "bg-white text-black"
                          : "bg-[#161616] text-gray-200 border border-[#252525]"
                      }`}
                    >
                      <p className="text-xs leading-relaxed whitespace-pre-wrap">{message.content}</p>
                      <p className="text-[10px] mt-1 opacity-60">
                        {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </p>
                    </div>
                    {message.role === "user" && (
                      <div className="w-6 h-6 bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] rounded-md flex items-center justify-center shrink-0">
                        <span className="text-white text-[10px] font-medium">U</span>
                      </div>
                    )}
                  </div>
                ))}

                {isTyping && (
                  <div className="flex gap-2 justify-start">
                    <div className="w-6 h-6 bg-[#161616] border border-[#252525] rounded-md flex items-center justify-center shrink-0">
                      <CubeIcon className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-[#161616] border border-[#252525] rounded-lg px-3 py-2">
                      <div className="flex gap-1">
                        <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" />
                        <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                        <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="p-4 border-t border-[#252525] bg-[#0a0a0a] rounded-b-2xl">
                <div className="flex gap-2">
                  <Textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask about your campaigns..."
                    className="min-h-[40px] max-h-[80px] resize-none bg-[#161616] border-[#252525] text-white text-xs placeholder:text-gray-600 focus-visible:ring-1 focus-visible:ring-white"
                    rows={1}
                  />
                  <Button
                    onClick={handleSend}
                    disabled={!input.trim() || isTyping}
                    size="sm"
                    className="bg-white hover:bg-gray-200 text-black px-3 shrink-0"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
                <p className="text-[10px] text-gray-600 text-center mt-2">
                  AI can make mistakes. Verify important info.
                </p>
              </div>
            </>
          )}
        </div>
      )}
    </>
  )
}
