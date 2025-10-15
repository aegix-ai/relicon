"use client"

import type React from "react"

import { useState, useEffect } from "react"
import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"
import { Mail, MessageSquare, Send, Menu, X, ChevronRight, MapPin } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  })
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

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
    console.log("[v0] Form submitted:", formData)
    // Handle form submission
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
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center space-y-4 text-center mb-16"
            >
              <Badge className="rounded-full px-4 py-1.5 text-sm font-medium" variant="secondary">
                Contact Us
              </Badge>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight">Get in Touch</h1>
              <p className="max-w-[800px] text-muted-foreground md:text-xl leading-relaxed">
                Have questions about Relicon? We'd love to hear from you. Send us a message and we'll respond as soon as
                possible.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-12 max-w-5xl mx-auto">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <Card className="border-border/40 bg-card backdrop-blur">
                  <CardContent className="p-8">
                    <h2 className="text-2xl font-bold mb-6">Send us a message</h2>
                    <form onSubmit={handleSubmit} className="space-y-6">
                      <div>
                        <label htmlFor="name" className="block text-sm font-medium mb-2">
                          Name
                        </label>
                        <Input
                          id="name"
                          placeholder="Your name"
                          value={formData.name}
                          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <label htmlFor="email" className="block text-sm font-medium mb-2">
                          Email
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
                        <label htmlFor="subject" className="block text-sm font-medium mb-2">
                          Subject
                        </label>
                        <Input
                          id="subject"
                          placeholder="What's this about?"
                          value={formData.subject}
                          onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <label htmlFor="message" className="block text-sm font-medium mb-2">
                          Message
                        </label>
                        <Textarea
                          id="message"
                          placeholder="Tell us more..."
                          rows={6}
                          value={formData.message}
                          onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                          required
                        />
                      </div>
                      <Button type="submit" className="w-full rounded-full" size="lg">
                        Send Message
                        <Send className="ml-2 size-4" />
                      </Button>
                    </form>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="space-y-8"
              >
                <div>
                  <h2 className="text-2xl font-bold mb-6">Other ways to reach us</h2>
                  <div className="space-y-6">
                    <Card className="border-border/40 bg-card backdrop-blur">
                      <CardContent className="p-6 flex items-start gap-4">
                        <div className="size-12 rounded-full bg-primary/20 flex items-center justify-center text-primary flex-shrink-0">
                          <Mail className="size-6" />
                        </div>
                        <div>
                          <h3 className="font-bold mb-1">Email</h3>
                          <p className="text-muted-foreground text-sm mb-2">For general inquiries</p>
                          <a
                            href="mailto:hello@getrelicon.com"
                            className="text-primary hover:underline text-sm font-medium"
                          >
                            hello@getrelicon.com
                          </a>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="border-border/40 bg-card backdrop-blur">
                      <CardContent className="p-6 flex items-start gap-4">
                        <div className="size-12 rounded-full bg-primary/20 flex items-center justify-center text-primary flex-shrink-0">
                          <MessageSquare className="size-6" />
                        </div>
                        <div>
                          <h3 className="font-bold mb-1">Support</h3>
                          <p className="text-muted-foreground text-sm mb-2">For technical support</p>
                          <a
                            href="mailto:hi@getrelicon.com"
                            className="text-primary hover:underline text-sm font-medium"
                          >
                            hi@getrelicon.com
                          </a>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="border-border/40 bg-card backdrop-blur">
                      <CardContent className="p-6 flex items-start gap-4">
                        <div className="size-12 rounded-full bg-primary/20 flex items-center justify-center text-primary flex-shrink-0">
                          <Mail className="size-6" />
                        </div>
                        <div>
                          <h3 className="font-bold mb-1">Team</h3>
                          <p className="text-muted-foreground text-sm mb-2">Reach our team directly</p>
                          <a
                            href="mailto:team@getrelicon.com"
                            className="text-primary hover:underline text-sm font-medium"
                          >
                            team@getrelicon.com
                          </a>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="border-border/40 bg-card backdrop-blur">
                      <CardContent className="p-6 flex items-start gap-4">
                        <div className="size-12 rounded-full bg-primary/20 flex items-center justify-center text-primary flex-shrink-0">
                          <MapPin className="size-6" />
                        </div>
                        <div>
                          <h3 className="font-bold mb-1">Location</h3>
                          <p className="text-muted-foreground text-sm">San Francisco, CA</p>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-bold mb-4">Connect With Us</h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <Link
                        href="https://www.linkedin.com/company/relicon/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-primary transition-colors"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="size-5"
                        >
                          <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                          <rect width="4" height="12" x="2" y="9"></rect>
                          <circle cx="4" cy="4" r="2"></circle>
                        </svg>
                      </Link>
                      <span className="text-sm text-muted-foreground">Relicon on LinkedIn</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Link
                        href="https://www.linkedin.com/company/aegixtech/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-primary transition-colors"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="size-5"
                        >
                          <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                          <rect width="4" height="12" x="2" y="9"></rect>
                          <circle cx="4" cy="4" r="2"></circle>
                        </svg>
                      </Link>
                      <span className="text-sm text-muted-foreground">Aegix (Parent Company) on LinkedIn</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Link
                        href="https://www.youtube.com/@AegixTech"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-primary transition-colors"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="currentColor"
                          className="size-5"
                        >
                          <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93-.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"></path>
                        </svg>
                      </Link>
                      <span className="text-sm text-muted-foreground">AegixTech on YouTube</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Link
                        href="https://www.instagram.com/aegix.group/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-primary transition-colors"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="size-5"
                        >
                          <rect width="20" height="20" x="2" y="2" rx="5" ry="5"></rect>
                          <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                          <line x1="17.5" x2="17.51" y1="6.5" y2="6.5"></line>
                        </svg>
                      </Link>
                      <span className="text-sm text-muted-foreground">Aegix Group on Instagram</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Link
                        href="https://www.tiktok.com/@aegix.group"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-primary transition-colors"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="currentColor"
                          className="size-5"
                        >
                          <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"></path>
                        </svg>
                      </Link>
                      <span className="text-sm text-muted-foreground">Aegix Group on TikTok</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-bold mb-4">Frequently Asked Questions</h3>
                  <p className="text-muted-foreground leading-relaxed mb-4">
                    Before reaching out, you might find your answer in our FAQ section on the homepage.
                  </p>
                  <Link href="/#faq">
                    <Button variant="outline" className="rounded-full bg-transparent">
                      View FAQ
                    </Button>
                  </Link>
                </div>
              </motion.div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
