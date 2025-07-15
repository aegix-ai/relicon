"use client"

import { useEffect } from "react"
import { useSearchParams } from "next/navigation"

export default function ShopifyCallback() {
  const searchParams = useSearchParams()
  
  useEffect(() => {
    const code = searchParams.get("code")
    const error = searchParams.get("error")
    
    if (code) {
      // Success - send code to parent window
      window.opener?.postMessage({
        type: "oauth_success",
        platform: "shopify",
        code: code
      }, "*")
      window.close()
    } else if (error) {
      // Error - send error to parent window
      window.opener?.postMessage({
        type: "oauth_error",
        platform: "shopify",
        error: error
      }, "*")
      window.close()
    }
  }, [searchParams])

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-white">Connecting your Shopify account...</p>
      </div>
    </div>
  )
}