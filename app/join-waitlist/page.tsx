"use client"

import type React from "react"

import { useState, useEffect } from "react"
import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"
import { ArrowRight, Check, Menu, X, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

export default function JoinWaitlistPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    monthlyAdSpend: "",
    primaryGoal: "",
  })
  const [submitted, setSubmitted] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      const response = await fetch('/api/waitlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to join waitlist')
      }

      setSubmitted(true)
    } catch (err: any) {
      setError(err.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
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

      <main className="flex-1">
        <section className="w-full py-20 md:py-32">
          <div className="container px-4 md:px-6">
            <div className="max-w-2xl mx-auto">
              {!submitted ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <div className="text-center mb-12">
                    <Badge className="rounded-full px-4 py-1.5 text-sm font-medium mb-4" variant="secondary">
                      Join Waitlist
                    </Badge>
                    <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
                      Be Among the First to Experience Relicon
                    </h1>
                    <p className="text-muted-foreground md:text-xl leading-relaxed">
                      Join our exclusive waitlist and get early access to advertising that learns, adapts, and
                      compounds.
                    </p>
                  </div>

                  <Card className="border-border/40 bg-card backdrop-blur shadow-xl">
                    <CardContent className="p-8">
                      <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                          <label htmlFor="name" className="block text-sm font-medium mb-2">
                            Full Name *
                          </label>
                          <Input
                            id="name"
                            placeholder="John Doe"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            required
                          />
                        </div>
                        <div>
                          <label htmlFor="email" className="block text-sm font-medium mb-2">
                            Email Address *
                          </label>
                          <Input
                            id="email"
                            type="email"
                            placeholder="john@company.com"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            required
                          />
                        </div>
                        <div>
                          <label htmlFor="company" className="block text-sm font-medium mb-2">
                            Company Name (Optional)
                          </label>
                          <Input
                            id="company"
                            placeholder="Your Company"
                            value={formData.company}
                            onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                          />
                        </div>
                        <div>
                          <label htmlFor="monthlyAdSpend" className="block text-sm font-medium mb-2">
                            Monthly Ad Spend (Optional)
                          </label>
                          <Input
                            id="monthlyAdSpend"
                            placeholder="e.g., $5,000"
                            value={formData.monthlyAdSpend}
                            onChange={(e) => setFormData({ ...formData, monthlyAdSpend: e.target.value })}
                          />
                        </div>
                        <div>
                          <label htmlFor="primaryGoal" className="block text-sm font-medium mb-2">
                            Primary Advertising Goal (Optional)
                          </label>
                          <Input
                            id="primaryGoal"
                            placeholder="e.g., Lead generation, Brand awareness"
                            value={formData.primaryGoal}
                            onChange={(e) => setFormData({ ...formData, primaryGoal: e.target.value })}
                          />
                        </div>
                        {error && (
                          <div className="text-sm text-red-500 p-3 bg-red-500/10 rounded-lg">
                            {error}
                          </div>
                        )}
                        <Button type="submit" className="w-full rounded-full" size="lg" disabled={loading}>
                          {loading ? "Joining..." : "Join Waitlist"}
                          {!loading && <ArrowRight className="ml-2 size-4" />}
                        </Button>
                      </form>

                      <div className="mt-8 pt-8 border-t border-border/40">
                        <h3 className="font-bold mb-4">What you'll get:</h3>
                        <ul className="space-y-3">
                          {[
                            "Early access to Relicon's self-improving ad engine",
                            "Exclusive onboarding and priority support",
                            "Special launch pricing for early adopters",
                            "Direct line to our product team for feedback",
                          ].map((benefit, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <Check className="size-5 text-primary mt-0.5 flex-shrink-0" />
                              <span className="text-sm text-muted-foreground">{benefit}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5 }}
                  className="text-center"
                >
                  <div className="size-20 rounded-full bg-green-500/20 flex items-center justify-center text-green-500 mx-auto mb-6">
                    <Check className="size-10" />
                  </div>
                  <h1 className="text-4xl font-bold tracking-tight mb-4">You're on the list!</h1>
                  <p className="text-muted-foreground md:text-lg leading-relaxed mb-8 max-w-lg mx-auto">
                    Thank you for joining the Relicon waitlist. We'll be in touch soon with exclusive early access
                    details.
                  </p>
                  <Link href="/">
                    <Button className="rounded-full">
                      Explore Relicon
                      <ArrowRight className="ml-2 size-4" />
                    </Button>
                  </Link>
                </motion.div>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
