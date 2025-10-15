"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"
import { Target, Users, Zap, Menu, X, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function AboutPage() {
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
        <section className="w-full py-12 md:py-16">
          <div className="container px-4 md:px-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center space-y-4 text-center mb-16"
            >
              <Badge className="rounded-full px-4 py-1.5 text-sm font-medium" variant="secondary">
                About Us
              </Badge>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight">Building the Future of Advertising</h1>
              <p className="max-w-[800px] text-muted-foreground md:text-xl leading-relaxed">
                Where intelligence compounds, outcomes matter, and growth is engineered.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="max-w-4xl mx-auto mb-20"
            >
              <div className="space-y-6 text-muted-foreground leading-relaxed">
                <p>
                  Relicon began with a simple realization. Brands were drowning in ads that looked good but did not
                  work. Agencies sold hours. Tools sold dashboards. None of them sold outcomes. We knew something
                  fundamental was broken.
                </p>

                <p>
                  The answer was not more templates or more consultants. It was a system that could learn. A machine
                  that would not just deliver, but improve itself every time it ran. That idea became Relicon. An engine
                  for compounding growth, built not as another tool but as an inevitability.
                </p>

                <p>
                  The journey started in silence. No press, no stage, no hype. Just nights spent asking what the future
                  of advertising should feel like if it were invented today. Every part of Relicon reflects that search
                  for first principles. Strip away everything that does not matter. Keep only what compounds. Build for
                  outcomes. Refuse to compromise.
                </p>

                <p>
                  We are not here to follow trends. We are here to build what should exist. The world does not need
                  another dashboard. It needs a new standard. That is why Relicon exists. A company born from
                  frustration, sharpened by vision, and obsessed with a single goal: to engineer influence itself.
                </p>
              </div>
            </motion.div>

            <div className="max-w-4xl mx-auto mb-20 pt-14 border-t border-white/10">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                <h2 className="text-3xl font-bold mb-6">Our Mission</h2>
                <p className="text-muted-foreground leading-relaxed text-lg">
                  To build the first advertising system that learns, adapts, and compounds results without human
                  intervention. To replace guesswork with certainty. To make performance advertising inevitable.
                </p>
              </motion.div>
            </div>

            <div className="grid md:grid-cols-3 gap-8 mb-20">
              {[
                {
                  icon: <Target className="size-6" />,
                  title: "Outcome-Focused",
                  description:
                    "We optimize for real business outcomes, not vanity metrics. Your success is our only metric.",
                },
                {
                  icon: <Zap className="size-6" />,
                  title: "Self-Improving",
                  description:
                    "Our engine learns and adapts automatically, getting smarter with every campaign you run.",
                },
                {
                  icon: <Users className="size-6" />,
                  title: "Customer-First",
                  description:
                    "We're building for growth-focused teams who demand results, not excuses or empty promises.",
                },
              ].map((value, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.4 + i * 0.1 }}
                >
                  <Card className="h-full border-border/40 bg-card backdrop-blur">
                    <CardContent className="p-6">
                      <div className="size-12 rounded-full bg-primary/20 flex items-center justify-center text-primary mb-4">
                        {value.icon}
                      </div>
                      <h3 className="text-xl font-bold mb-2">{value.title}</h3>
                      <p className="text-muted-foreground leading-relaxed">{value.description}</p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.7 }}
              className="text-center"
            >
              <h2 className="text-3xl font-bold mb-4">Join Us on This Journey</h2>
              <p className="text-muted-foreground md:text-lg leading-relaxed mb-8 max-w-2xl mx-auto">
                We're just getting started. Join our waitlist to be among the first to experience advertising that
                learns, adapts, and compounds.
              </p>
              <Link href="/join-waitlist">
                <Button size="lg" className="rounded-full">
                  Join Waitlist
                </Button>
              </Link>
            </motion.div>
          </div>
        </section>
      </main>
    </div>
  )
}
