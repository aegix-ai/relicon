"use client"

import { useState, useEffect } from "react"
import { Send, ChevronRight, ChevronLeft, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import { CubeIcon } from "@/components/icons/CubeIcon"
import { toast } from "sonner"

interface Message {
  role: "user" | "assistant"
  content: string
}

const sampleMessages: Message[] = [
  {
    role: "assistant",
    content: "Hi! I'm Relicon AI. I can help you analyze your ad performance, answer questions about your campaigns, and provide insights on CTR, ROAS, conversions, and more. What would you like to know?",
  },
]

export function ChatPanel() {
  const [isMobile, setIsMobile] = useState(false)
  const [isBarCollapsed, setIsBarCollapsed] = useState(false)
  const [isPanelOpen, setIsPanelOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>(sampleMessages)
  const [input, setInput] = useState("")
  const [barInput, setBarInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)

  // TODO: Get user ID from authentication
  const userId = null // Replace with auth.user?.id when auth is implemented

  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 640
      setIsMobile(mobile)
      if (mobile) {
        setIsBarCollapsed(true)
      }
    }

    checkMobile()
    window.addEventListener("resize", checkMobile)
    return () => window.removeEventListener("resize", checkMobile)
  }, [])

  const handleSend = async () => {
    if (!input.trim() || isTyping) return

    const userMessage = { role: "user" as const, content: input }
    setMessages([...messages, userMessage])
    setInput("")
    setIsTyping(true)

    try {
      // Prepare conversation history
      const conversationHistory = messages
        .slice(1) // Skip initial greeting
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }))

      conversationHistory.push({
        role: userMessage.role,
        content: userMessage.content
      })

      // Call chat API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: conversationHistory,
          userId: userId
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get response')
      }

      // Add AI response
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.message,
        },
      ])
    } catch (error: any) {
      console.error('Chat error:', error)
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I apologize, but I encountered an error. Please make sure your OpenAI API key is configured and try again.",
        },
      ])
      toast.error('Failed to send message')
    } finally {
      setIsTyping(false)
    }
  }

  const handleBarSend = async () => {
    if (!barInput.trim() || isTyping) return

    const userMessage = { role: "user" as const, content: barInput }
    setMessages([...messages, userMessage])
    setIsPanelOpen(true)
    setBarInput("")
    setIsTyping(true)

    try {
      // Prepare conversation history
      const conversationHistory = messages
        .slice(1) // Skip initial greeting
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }))

      conversationHistory.push({
        role: userMessage.role,
        content: userMessage.content
      })

      // Call chat API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: conversationHistory,
          userId: userId
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get response')
      }

      // Add AI response
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.message,
        },
      ])
    } catch (error: any) {
      console.error('Chat error:', error)
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I apologize, but I encountered an error. Please try again.",
        },
      ])
      toast.error('Failed to send message')
    } finally {
      setIsTyping(false)
    }
  }

  const handleCollapsedClick = () => {
    if (isMobile) {
      setIsPanelOpen(true)
    } else {
      setIsBarCollapsed(false)
    }
  }

  return (
    <>
      {!isBarCollapsed && !isPanelOpen && !isMobile && (
        <div className="fixed bottom-4 sm:bottom-6 right-4 sm:right-6 w-[calc(100%-2rem)] sm:w-96 max-w-md z-40">
          <div className="relative flex items-center gap-0 bg-[#1c1c1c] rounded-lg border border-[#2f2f2f] shadow-2xl overflow-hidden">
            <div className="relative flex-1">
              <Input
                value={barInput}
                onChange={(e) => setBarInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleBarSend()}
                placeholder="Ask Relicon AI anything..."
                className="w-full h-11 sm:h-12 pl-10 sm:pl-12 pr-4 bg-transparent border-0 text-gray-200 placeholder:text-gray-500 focus:ring-0 focus:outline-none text-sm sm:text-base"
              />
              <div className="absolute left-3 sm:left-4 top-1/2 -translate-y-1/2">
                <CubeIcon className="w-4 h-4 sm:w-5 sm:h-5 text-gray-400" />
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsBarCollapsed(true)}
              className="h-11 w-11 sm:h-12 sm:w-12 shrink-0 hover:bg-[#252525] text-gray-400 hover:text-white rounded-none border-l border-[#2f2f2f]"
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}

      {(isBarCollapsed || isMobile) && !isPanelOpen && (
        <Button
          onClick={handleCollapsedClick}
          className="fixed bottom-4 sm:bottom-6 right-4 sm:right-6 h-11 sm:h-12 px-3 sm:px-4 bg-[#1c1c1c] hover:bg-[#252525] border border-[#2f2f2f] text-gray-300 hover:text-white rounded-lg shadow-2xl z-40 text-sm sm:text-base"
        >
          <CubeIcon className="w-4 h-4 sm:w-5 sm:h-5 mr-2 text-gray-400" />
          <span className="text-sm">Ask AI</span>
          <ChevronLeft className="w-4 h-4 ml-2" />
        </Button>
      )}

      <div
        className={cn(
          "fixed top-0 right-0 h-screen bg-[#0d0d0d] border-l border-[#2a2a2a] shadow-2xl transition-all duration-300 z-50 flex flex-col",
          isPanelOpen ? "w-full sm:w-96" : "w-0 overflow-hidden",
        )}
      >
        <div className="flex items-center justify-between p-4 border-b border-[#2a2a2a]">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#1a1a1a] rounded-lg flex items-center justify-center border border-[#2a2a2a]">
              <CubeIcon className="w-4 h-4 text-gray-300" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-200 text-sm">Relicon AI</h3>
              <p className="text-xs text-gray-500">Always here to help</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsPanelOpen(false)}
            className="h-8 w-8 text-gray-400 hover:text-gray-200 hover:bg-[#1a1a1a]"
          >
            {isMobile ? <X className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div key={index} className={cn("flex", message.role === "user" ? "justify-end" : "justify-start")}>
              <div
                className={cn(
                  "max-w-[80%] rounded-xl px-4 py-2.5 text-sm",
                  message.role === "user"
                    ? "bg-[#1a1a1a] text-white border border-[#2a2a2a]"
                    : "bg-[#161616] text-gray-200 border border-[#2a2a2a]",
                )}
              >
                {message.content}
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-[#161616] border border-[#2a2a2a] rounded-xl px-4 py-2.5">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-[#2a2a2a]">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !isTyping && handleSend()}
              placeholder="Ask anything..."
              disabled={isTyping}
              className="rounded-lg bg-[#161616] border-[#2a2a2a] text-gray-200 placeholder:text-gray-500"
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isTyping}
              size="icon"
              className="bg-[#1a1a1a] hover:bg-[#252525] border border-[#2a2a2a] text-white rounded-lg shrink-0 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {isPanelOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40" onClick={() => setIsPanelOpen(false)} />
      )}
    </>
  )
}
