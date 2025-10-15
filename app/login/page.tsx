"use client"

import type React from "react"

import { useState, useEffect } from "react"
import Link from "next/link"
import Image from "next/image"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { ArrowRight, Menu, X, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

export default function LoginPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  })
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    const VALID_EMAIL = "team@getrelicon.com"
    const VALID_PASSWORD = "Relicon123456"

    if (formData.email !== VALID_EMAIL || formData.password !== VALID_PASSWORD) {
      setError("Invalid email or password. Please try again.")
      setLoading(false)
      return
    }

    router.push("/dashboard")
  }

  return (
    <div className="flex min-h-[100dvh] flex-col">
      <header
        className={`sticky top-0 z-50 w-full backdrop-blur-lg transition-all duration-300 ${isScrolled ? "bg-background/80 shadow-sm border-b border-border/40" : "bg-transparent"}`}
      >
        <div className="container flex h-16 items-center justify-between">
          <Link
            href="/"
            className="flex items-center gap-3"
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          >
            <Image src="/relicon-full-logo.png" alt="Relicon" width={120} height={32} className="h-11 w-auto" />
          </Link>
          <nav className="hidden md:flex gap-8">
            <Link
              href="/#features"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Features
            </Link>
            <Link
              href="/#why-relicon"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Why Relicon
            </Link>
            <Link
              href="/#pricing"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Pricing
            </Link>
            <Link
              href="/about"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              About Us
            </Link>
            <Link
              href="/contact"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Contact Us
            </Link>
          </nav>
          <div className="hidden md:flex gap-3 items-center">
            <Link href="/login">
              <Button variant="ghost" className="rounded-full">
                Login
              </Button>
            </Link>
            <Link href="/join-waitlist">
              <Button className="rounded-full bg-primary hover:bg-primary/90">
                Join Waitlist
                <ChevronRight className="ml-1 size-4" />
              </Button>
            </Link>
          </div>
          <div className="flex items-center gap-4 md:hidden">
            <Button variant="ghost" size="icon" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X className="size-5" /> : <Menu className="size-5" />}
              <span className="sr-only">Toggle menu</span>
            </Button>
          </div>
        </div>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="md:hidden absolute top-16 inset-x-0 bg-background/95 backdrop-blur-lg border-b"
          >
            <div className="container py-4 flex flex-col gap-4">
              <Link href="/#features" className="py-2 text-sm font-medium" onClick={() => setMobileMenuOpen(false)}>
                Features
              </Link>
              <Link href="/#why-relicon" className="py-2 text-sm font-medium" onClick={() => setMobileMenuOpen(false)}>
                Why Relicon
              </Link>
              <Link href="/#pricing" className="py-2 text-sm font-medium" onClick={() => setMobileMenuOpen(false)}>
                Pricing
              </Link>
              <Link href="/about" className="py-2 text-sm font-medium" onClick={() => setMobileMenuOpen(false)}>
                About Us
              </Link>
              <Link href="/contact" className="py-2 text-sm font-medium" onClick={() => setMobileMenuOpen(false)}>
                Contact Us
              </Link>
              <div className="flex flex-col gap-2 pt-2 border-t">
                <Link href="/login">
                  <Button variant="ghost" className="rounded-full w-full">
                    Login
                  </Button>
                </Link>
                <Link href="/join-waitlist">
                  <Button className="rounded-full bg-primary hover:bg-primary/90 w-full">
                    Join Waitlist
                    <ChevronRight className="ml-1 size-4" />
                  </Button>
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </header>

      <main className="flex-1 flex items-center justify-center py-20">
        <div className="container px-4 md:px-6">
          <div className="max-w-md mx-auto">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
              <div className="text-center mb-8">
                <Badge className="rounded-full px-4 py-1.5 text-sm font-medium mb-4" variant="secondary">
                  Login
                </Badge>
                <h1 className="text-3xl md:text-4xl font-bold tracking-tight mb-2">Welcome Back</h1>
                <p className="text-muted-foreground">Sign in to access your Relicon dashboard</p>
              </div>

              <Card className="border-border/40 bg-card backdrop-blur shadow-xl">
                <CardContent className="p-8">
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium mb-2">
                        Email Address
                      </label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="your@email.com"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor="password" className="block text-sm font-medium mb-2">
                        Password
                      </label>
                      <Input
                        id="password"
                        type="password"
                        placeholder="••••••••"
                        value={formData.password}
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        required
                      />
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" className="rounded border-border" />
                        <span className="text-muted-foreground">Remember me</span>
                      </label>
                      <Link href="#" className="text-primary hover:underline">
                        Forgot password?
                      </Link>
                    </div>
                    {error && (
                      <div className="text-sm text-red-500 p-3 bg-red-500/10 rounded-lg">
                        {error}
                      </div>
                    )}
                    <Button type="submit" className="w-full rounded-full" size="lg" disabled={loading}>
                      {loading ? "Signing in..." : "Sign In"}
                      {!loading && <ArrowRight className="ml-2 size-4" />}
                    </Button>
                  </form>

                  <div className="mt-6 text-center text-sm text-muted-foreground">
                    Don't have an account?{" "}
                    <Link href="/join-waitlist" className="text-primary hover:underline font-medium">
                      Join the waitlist
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </main>
    </div>
  )
}
