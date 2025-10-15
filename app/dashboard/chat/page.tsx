"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Send, Paperclip, ImageIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { CubeIcon } from "@/components/icons/CubeIcon"

interface Message {
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

const initialMessages: Message[] = [
  {
    role: "assistant",
    content:
      "Hello! I'm Relicon AI, your creative advertising assistant. I can help you plan campaigns, generate ad creatives, analyze performance, and answer any questions about your advertising strategy. How can I assist you today?",
    timestamp: new Date(),
  },
]

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = () => {
    if (!input.trim()) return

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsTyping(true)

    setTimeout(() => {
      const aiMessage: Message = {
        role: "assistant",
        content:
          "I understand you're looking for help with that. In the full version, I would provide detailed insights, campaign suggestions, and creative recommendations based on your needs. Feel free to ask me anything about your advertising strategy!",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])
      setIsTyping(false)
    }, 1500)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="h-screen flex flex-col bg-[#0a0a0a]">
      <div className="border-b border-[#1f1f1f] bg-[#0d0d0d] px-6 xl:px-8 py-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#161616] border border-[#252525] rounded-xl flex items-center justify-center">
            <CubeIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white">Relicon AI</h1>
            <p className="text-sm text-gray-500">Your creative advertising assistant</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6 xl:px-8 py-6">
        <div className="xl:max-w-none max-w-4xl mx-auto space-y-6">
          {messages.map((message, index) => (
            <div key={index} className={`flex gap-4 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
              {message.role === "assistant" && (
                <div className="w-8 h-8 bg-[#161616] border border-[#252525] rounded-lg flex items-center justify-center shrink-0">
                  <CubeIcon className="w-5 h-5 text-white" />
                </div>
              )}
              <div
                className={`max-w-[70%] rounded-2xl px-5 py-3 ${
                  message.role === "user"
                    ? "bg-[#1a1a1a] text-white border border-[#252525]"
                    : "bg-[#161616] text-gray-200 border border-[#252525]"
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                <p className="text-xs mt-2 opacity-60">
                  {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </p>
              </div>
              {message.role === "user" && (
                <div className="w-8 h-8 bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] rounded-lg flex items-center justify-center shrink-0">
                  <span className="text-white text-sm font-medium">U</span>
                </div>
              )}
            </div>
          ))}

          {isTyping && (
            <div className="flex gap-4 justify-start">
              <div className="w-8 h-8 bg-[#161616] border border-[#252525] rounded-lg flex items-center justify-center shrink-0">
                <CubeIcon className="w-5 h-5 text-white" />
              </div>
              <div className="bg-[#161616] border border-[#252525] rounded-2xl px-5 py-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <div
                    className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                    style={{ animationDelay: "150ms" }}
                  />
                  <div
                    className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                    style={{ animationDelay: "300ms" }}
                  />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="border-t border-[#1f1f1f] bg-[#0d0d0d] px-6 xl:px-8 py-4">
        <div className="xl:max-w-none max-w-4xl mx-auto">
          <div className="relative bg-[#161616] border border-[#252525] rounded-2xl p-4">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask Relicon AI anything... (Shift + Enter for new line)"
              className="min-h-[60px] max-h-[200px] resize-none bg-transparent border-0 text-gray-200 placeholder:text-gray-600 focus-visible:ring-0 focus-visible:ring-offset-0 p-0"
            />

            <div className="flex items-center justify-between mt-3 pt-3 border-t border-[#252525]">
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 text-gray-500 hover:text-gray-300 hover:bg-[#1f1f1f]"
                >
                  <Paperclip className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 text-gray-500 hover:text-gray-300 hover:bg-[#1f1f1f]"
                >
                  <ImageIcon className="w-4 h-4" />
                </Button>
              </div>

              <Button
                onClick={handleSend}
                disabled={!input.trim()}
                className="bg-white hover:bg-gray-200 text-black rounded-lg px-6 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4 mr-2" />
                Send
              </Button>
            </div>
          </div>

          <p className="text-xs text-gray-600 text-center mt-3">
            Relicon AI can make mistakes. Consider checking important information.
          </p>
        </div>
      </div>
    </div>
  )
}
