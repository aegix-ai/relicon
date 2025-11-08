"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"
import { Check, ChevronRight, Menu, X, ArrowRight, Star, Zap, BarChart, TrendingUp, Target, Brain } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { ScrollToTop } from "@/components/scroll-to-top"

export default function LandingPage() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setIsScrolled(true)
      } else {
        setIsScrolled(false)
      }
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  }

  const features = [
    {
      title: "Self-Improving Ads",
      description: "Your advertising learns and adapts automatically, getting smarter with every campaign.",
      icon: <Brain className="size-5" />,
    },
    {
      title: "Outcome-Based Optimization",
      description: "Connected directly to outcomes, not vanity metrics. Real results that matter.",
      icon: <Target className="size-5" />,
    },
    {
      title: "Compounding Growth",
      description: "Designed for exponential growth. Every dollar becomes smarter over time.",
      icon: <TrendingUp className="size-5" />,
    },
    {
      title: "Advanced Analytics",
      description: "Enterprise-grade analytics to track and understand your growth trajectory.",
      icon: <BarChart className="size-5" />,
    },
    {
      title: "Automated Learning",
      description: "No manual optimization required. The engine learns and improves continuously.",
      icon: <Zap className="size-5" />,
    },
    {
      title: "Priority Support",
      description: "Get help when you need it with dedicated support for your growth journey.",
      icon: <Star className="size-5" />,
    },
  ]

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
              href="#features"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Features
            </Link>
            <Link
              href="#why-relicon"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Why Relicon
            </Link>
            <Link
              href="#pricing"
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
        {/* Mobile menu */}
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="md:hidden absolute top-16 inset-x-0 bg-background/95 backdrop-blur-lg border-b"
          >
            <div className="container py-4 flex flex-col gap-4">
              <Link href="#features" className="py-2 text-sm font-medium" onClick={() => setMobileMenuOpen(false)}>
                Features
              </Link>
              <Link href="#why-relicon" className="py-2 text-sm font-medium" onClick={() => setMobileMenuOpen(false)}>
                Why Relicon
              </Link>
              <Link href="#pricing" className="py-2 text-sm font-medium" onClick={() => setMobileMenuOpen(false)}>
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
        <section className="w-full py-20 md:py-24 lg:py-28 pb-12 md:pb-16 overflow-hidden">
          <div className="container px-4 md:px-6 relative">
            <div className="absolute inset-0 -z-10 h-full w-full bg-background bg-[linear-gradient(to_right,#1f1f1f_1px,transparent_1px),linear-gradient(to_bottom,#1f1f1f_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_110%)]"></div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center max-w-3xl mx-auto mb-12"
            >
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 pb-2 leading-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
                Influence, Engineered.
              </h1>
              <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
                Your advertising learns, adapts, and compounds. Every dollar becomes smarter. Growth isn't a gamble,
                it's a certainty built on intelligence that evolves. This is Relicon.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/join-waitlist">
                  <Button size="lg" className="rounded-full h-12 px-8 text-base bg-primary hover:bg-primary/90">
                    Join Waitlist
                    <ArrowRight className="ml-2 size-4" />
                  </Button>
                </Link>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.2 }}
              className="relative mx-auto max-w-5xl mt-8"
            >
              {/* macOS window chrome with three colored dots */}
              <div className="relative rounded-xl overflow-hidden shadow-2xl border border-white/10 bg-zinc-900/90 backdrop-blur-sm">
                {/* macOS window header with traffic lights */}
                <div className="flex items-center gap-2 px-4 py-3 bg-zinc-800/80 border-b border-white/5">
                  <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500 hover:bg-red-600 transition-colors"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-600 transition-colors"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500 hover:bg-green-600 transition-colors"></div>
                  </div>
                  <div className="flex-1 text-center text-xs text-zinc-400 font-medium">Relicon Dashboard</div>
                  <div className="w-16"></div> {/* Spacer for centering */}
                </div>

                {/* Dashboard screenshot */}
                <div className="bg-zinc-950">
                  <Image
                    src="/images/dashboard-screenshot-v2.png"
                    width={1440}
                    height={720}
                    alt="Relicon dashboard showing performance analytics"
                    className="w-full h-auto"
                    priority
                  />
                </div>

                {/* Subtle inner glow */}
                <div className="absolute inset-0 rounded-xl ring-1 ring-inset ring-white/5 pointer-events-none"></div>
              </div>
              {/* Floating card glow effects */}
              <div className="absolute -bottom-8 -right-8 -z-10 h-[400px] w-[400px] rounded-full bg-gradient-to-br from-cyan-900/30 to-blue-900/20 blur-3xl opacity-60"></div>
              <div className="absolute -top-8 -left-8 -z-10 h-[400px] w-[400px] rounded-full bg-gradient-to-br from-purple-900/30 to-blue-900/20 blur-3xl opacity-60"></div>
            </motion.div>
          </div>
        </section>

        <section id="features" className="w-full pt-8 md:pt-12 pb-16 md:pb-24">
          <div className="container px-4 md:px-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center space-y-4 text-center mb-12"
            >
              <Badge className="rounded-full px-4 py-1.5 text-sm font-medium" variant="secondary">
                Features
              </Badge>
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight">Intelligence That Evolves</h2>
              <p className="max-w-[800px] text-muted-foreground md:text-lg leading-relaxed">
                Our Self-Improving Ad Director provides all the tools you need to achieve compounding growth and
                maximize your advertising ROI.
              </p>
            </motion.div>

            <motion.div
              variants={container}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true }}
              className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
            >
              {features.map((feature, i) => (
                <motion.div key={i} variants={item}>
                  <Card className="h-full overflow-hidden border-border/40 bg-card backdrop-blur transition-all hover:shadow-lg hover:border-primary/50">
                    <CardContent className="p-6 flex flex-col h-full">
                      <div className="size-10 rounded-full bg-primary/20 flex items-center justify-center text-primary mb-4">
                        {feature.icon}
                      </div>
                      <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                      <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        <section id="why-relicon" className="w-full py-20 md:py-32 bg-muted/30 relative overflow-hidden">
          <div className="absolute inset-0 -z-10 h-full w-full bg-background bg-[linear-gradient(to_right,#1f1f1f_1px,transparent_1px),linear-gradient(to_bottom,#1f1f1f_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,#000_40%,transparent_100%)]"></div>

          <div className="container px-4 md:px-6 relative">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center space-y-4 text-center mb-12"
            >
              <Badge className="rounded-full px-4 py-1.5 text-sm font-medium" variant="secondary">
                Why Relicon
              </Badge>
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight">The Relicon Advantage</h2>
              <p className="max-w-[800px] text-muted-foreground md:text-lg leading-relaxed">
                Traditional approaches versus the Relicon advantage
              </p>
            </motion.div>

            <div className="grid gap-6 md:grid-cols-3 max-w-5xl mx-auto">
              {[
                {
                  title: "Agencies/Freelancers",
                  items: [
                    "Expensive retainers",
                    "Manual, slow iterations",
                    "Results not guaranteed",
                    "High overhead costs",
                  ],
                  negative: true,
                },
                {
                  title: "Generic Tools",
                  items: [
                    "Random outputs with no strategic direction",
                    "Low quality, generic content",
                    "No learning or improvement over time",
                    "No intelligence behind creation",
                    "Requires constant manual optimization",
                  ],
                  negative: true,
                },
                {
                  title: "Relicon",
                  items: [
                    "Self-improving ad engine",
                    "Connects directly to outcomes, not vanity metrics",
                    "Designed for compounding growth",
                    "Automated optimization and learning",
                  ],
                  negative: false,
                },
              ].map((comparison, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                >
                  <Card
                    className={`h-full overflow-hidden ${comparison.negative ? "border-border/40 bg-card" : "border-green-800/40 bg-white shadow-xl"} backdrop-blur transition-all hover:shadow-lg hover:border-primary/50`}
                  >
                    <CardContent className="p-6 flex flex-col h-full">
                      <h3 className={`text-xl font-bold mb-4 ${!comparison.negative ? "text-black" : ""}`}>
                        {comparison.title}
                      </h3>
                      <ul className="space-y-3">
                        {comparison.items.map((item, j) => (
                          <li key={j} className="flex items-start gap-2">
                            {comparison.negative ? (
                              <X className="size-4 text-red-900 mt-0.5 flex-shrink-0" />
                            ) : (
                              <Check className="size-4 text-green-600 mt-0.5 flex-shrink-0" />
                            )}
                            <span className={comparison.negative ? "text-muted-foreground" : "text-gray-700"}>
                              {item}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="w-full py-20 md:py-32">
          <div className="container px-4 md:px-6 relative">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center space-y-6 text-center mb-16"
            >
              <Badge className="rounded-full px-4 py-1.5 text-sm font-medium" variant="secondary">
                How It Works
              </Badge>
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight">
                Simple Process, Powerful Results
              </h2>
              <p className="mx-auto max-w-[800px] text-muted-foreground md:text-xl leading-relaxed">
                Get started in minutes and see the difference our platform can make for your business.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8 md:gap-12 relative">
              <div className="hidden md:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-border to-transparent -translate-y-1/2 z-0"></div>

              {[
                {
                  step: "01",
                  title: "Create Account",
                  description: "Sign up in seconds with just your email. Start your journey to smarter advertising.",
                },
                {
                  step: "02",
                  title: "Configure Campaign",
                  description:
                    "Set up your first campaign with our intuitive interface. Connect your outcomes and goals.",
                },
                {
                  step: "03",
                  title: "Watch It Learn",
                  description: "Relicon learns from every interaction, continuously optimizing for better results.",
                },
              ].map((step, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                  className="relative z-10 flex flex-col items-center text-center space-y-4"
                >
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary/70 text-primary-foreground text-xl font-bold shadow-lg">
                    {step.step}
                  </div>
                  <h3 className="text-xl font-bold">{step.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">{step.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        <section id="pricing" className="w-full py-20 md:py-32 bg-muted/30 relative overflow-hidden">
          <div className="absolute inset-0 -z-10 h-full w-full bg-background bg-[linear-gradient(to_right,#1f1f1f_1px,transparent_1px),linear-gradient(to_bottom,#1f1f1f_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,#000_40%,transparent_100%)]"></div>

          <div className="container px-4 md:px-6 relative">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center space-y-4 text-center mb-12"
            >
              <Badge className="rounded-full px-4 py-1.5 text-sm font-medium" variant="secondary">
                Pricing
              </Badge>
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight">Choose Your Growth Trajectory</h2>
              <p className="max-w-[800px] text-muted-foreground md:text-lg leading-relaxed">
                Select the plan that fits your growth goals. Every plan includes our self-improving ad engine.
              </p>
            </motion.div>

            <div className="mx-auto max-w-5xl">
              <div className="grid gap-6 lg:grid-cols-3 lg:gap-8">
                {[
                  {
                    name: "Starter",
                    price: "$149",
                    period: "4 self improving ads",
                    description: "4 rounds of compounding ad growth through Relicon's self-improving engine.",
                    features: ["Self-Improving Ads", "Outcome-Based Optimization", "Basic Analytics", "Email Support"],
                    cta: "Get Started",
                  },
                  {
                    name: "Professional",
                    price: "$299",
                    period: "10 self improving ads",
                    description: "Accelerated growth with advanced optimization and priority support.",
                    features: [
                      "Self-Improving Ads",
                      "Outcome-Based Optimization",
                      "Advanced Analytics",
                      "Priority Support",
                      "Custom Integrations",
                    ],
                    cta: "Get Started",
                    popular: true,
                  },
                  {
                    name: "Enterprise",
                    price: "Custom",
                    period: "Unlimited self improving ads",
                    description: "Full-scale ad engine with dedicated support and custom solutions.",
                    features: [
                      "Self-Improving Ads",
                      "Outcome-Based Optimization",
                      "Enterprise Analytics",
                      "Dedicated Account Manager",
                      "Custom Integrations",
                      "White-Label Options",
                    ],
                    cta: "Get Started",
                  },
                ].map((plan, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: i * 0.1 }}
                  >
                    <Card
                      className={`relative overflow-hidden h-full ${plan.popular ? "border-blue-800/40 bg-white shadow-2xl" : "border-border/40 bg-card shadow-md"} backdrop-blur transition-all hover:shadow-2xl`}
                    >
                      {plan.popular && (
                        <div className="absolute top-0 right-0 bg-blue-600 text-white px-3 py-1 text-xs font-medium rounded-bl-lg">
                          Most Popular
                        </div>
                      )}
                      <CardContent className="p-6 flex flex-col h-full">
                        <h3 className={`text-2xl font-bold ${plan.popular ? "text-black" : ""}`}>{plan.name}</h3>
                        <div className="flex items-baseline mt-4">
                          <span className={`text-4xl font-bold ${plan.popular ? "text-black" : ""}`}>{plan.price}</span>
                          <span className={`ml-1 text-sm ${plan.popular ? "text-gray-600" : "text-muted-foreground"}`}>
                            / {plan.period}
                          </span>
                        </div>
                        <p
                          className={`mt-2 leading-relaxed ${plan.popular ? "text-gray-700" : "text-muted-foreground"}`}
                        >
                          {plan.description}
                        </p>
                        <ul className="space-y-3 my-6 flex-grow">
                          {plan.features.map((feature, j) => (
                            <li key={j} className="flex items-center">
                              <Check
                                className={`mr-2 size-4 flex-shrink-0 ${plan.popular ? "text-blue-600" : "text-primary"}`}
                              />
                              <span className={`text-sm ${plan.popular ? "text-gray-800" : ""}`}>{feature}</span>
                            </li>
                          ))}
                        </ul>
                        <Link href="/join-waitlist">
                          {plan.popular ? (
                            <button className="w-full mt-auto rounded-full h-10 px-4 py-2 inline-flex items-center justify-center whitespace-nowrap text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 !bg-white hover:!bg-gray-100 !text-black !border-2 !border-gray-300 shadow-sm">
                              {plan.cta}
                            </button>
                          ) : (
                            <Button className="w-full mt-auto rounded-full bg-transparent" variant="outline">
                              {plan.cta}
                            </Button>
                          )}
                        </Link>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section id="faq" className="w-full py-20 md:py-32">
          <div className="container px-4 md:px-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center space-y-4 text-center mb-12"
            >
              <Badge className="rounded-full px-4 py-1.5 text-sm font-medium" variant="secondary">
                FAQ
              </Badge>
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight">Frequently Asked Questions</h2>
              <p className="max-w-[800px] text-muted-foreground md:text-lg leading-relaxed">
                Find answers to common questions about our platform.
              </p>
            </motion.div>

            <div className="mx-auto max-w-3xl">
              <Accordion type="single" collapsible className="w-full">
                {[
                  {
                    question: "How does the self-improving engine work?",
                    answer:
                      "Relicon uses advanced machine learning to analyze your campaign performance in real-time. It identifies patterns, tests variations, and automatically optimizes for your specific outcomes. Unlike traditional tools, it gets better with every interaction.",
                  },
                  {
                    question: "Can I upgrade my plan later?",
                    answer:
                      "Yes, you can upgrade your plan at any time. If you upgrade, you'll get immediate access to additional features. Your unused loops from the previous plan will be credited to your account.",
                  },
                  {
                    question: "What outcomes can I optimize for?",
                    answer:
                      "You can optimize for any business outcome that matters to you - sales, sign-ups, engagement, retention, or custom metrics. Relicon connects directly to your outcomes, not vanity metrics like clicks or impressions.",
                  },
                  {
                    question: "How is this different from other ad platforms?",
                    answer:
                      "Traditional platforms require constant manual optimization and don't learn over time. Relicon's engine continuously improves itself, compounds your growth, and focuses on real business outcomes rather than surface-level metrics.",
                  },
                  {
                    question: "What kind of support do you offer?",
                    answer:
                      "Support varies by plan. Starter includes email support, Professional includes priority support with faster response times, and Enterprise includes a dedicated account manager with 24/7 availability.",
                  },
                ].map((faq, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.3, delay: i * 0.05 }}
                  >
                    <AccordionItem value={`item-${i}`} className="border-b border-border/40 py-2">
                      <AccordionTrigger className="text-left font-medium hover:no-underline">
                        {faq.question}
                      </AccordionTrigger>
                      <AccordionContent className="text-muted-foreground leading-relaxed">
                        {faq.answer}
                      </AccordionContent>
                    </AccordionItem>
                  </motion.div>
                ))}
              </Accordion>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="w-full py-20 md:py-32 bg-gradient-to-br from-primary to-primary/80 text-primary-foreground relative overflow-hidden">
          <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#ffffff10_1px,transparent_1px),linear-gradient(to_bottom,#ffffff10_1px,transparent_1px)] bg-[size:4rem_4rem]"></div>
          <div className="absolute -top-24 -left-24 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>

          <div className="container px-4 md:px-6 relative">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center space-y-6 text-center"
            >
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight">We've Been Where You Are</h2>
              <p className="mx-auto max-w-[700px] text-primary-foreground/90 md:text-xl leading-relaxed">
                Late nights staring at dashboards. Budgets burning on guesswork. Not knowing what works or why. We lived
                it. That's why we built Relicon. From the trenches of small budgets and big dreams. We created the
                system we needed, one that learns and turns advertising from a gamble into a science.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 mt-4">
                <Link href="/join-waitlist">
                  <Button size="lg" variant="secondary" className="rounded-full h-12 px-8 text-base">
                    Join the Movement
                    <ArrowRight className="ml-2 size-4" />
                  </Button>
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
      </main>
      <footer className="w-full border-t bg-card/50 backdrop-blur-sm">
        <div className="container flex flex-col gap-8 px-4 py-10 md:px-6 lg:py-16">
          <div className="grid gap-8 sm:grid-cols-2 md:grid-cols-4">
            <div className="space-y-4">
              <Link href="/" className="flex items-center gap-3">
                <Image src="/relicon-full-logo.png" alt="Relicon" width={120} height={32} className="h-12 w-auto" />
              </Link>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Influence, engineered. Your advertising learns, adapts, and compounds for guaranteed growth.
              </p>
              <div className="flex gap-4">
                <Link
                  href="https://www.linkedin.com/company/relicon/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                  title="LinkedIn"
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
                  <span className="sr-only">LinkedIn</span>
                </Link>
                <Link
                  href="https://www.youtube.com/@AegixTech"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    className="size-5"
                  >
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93-.502 5.814a3.016 3.016 0 0 0 2.122 2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"></path>
                  </svg>
                  <span className="sr-only">YouTube</span>
                </Link>
                <Link
                  href="https://www.instagram.com/aegix.group/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground transition-colors"
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
                  <span className="sr-only">Instagram</span>
                </Link>
                <Link
                  href="https://www.tiktok.com/@aegix.group"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground transition-colors"
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
                  <span className="sr-only">TikTok</span>
                </Link>
              </div>
            </div>
            <div className="space-y-4">
              <h4 className="text-sm font-bold">Product</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="#features" className="text-muted-foreground hover:text-foreground transition-colors">
                    Features
                  </Link>
                </li>
                <li>
                  <Link href="#pricing" className="text-muted-foreground hover:text-foreground transition-colors">
                    Pricing
                  </Link>
                </li>
                <li>
                  <Link href="#why-relicon" className="text-muted-foreground hover:text-foreground transition-colors">
                    Why Relicon
                  </Link>
                </li>
                <li>
                  <Link href="#faq" className="text-muted-foreground hover:text-foreground transition-colors">
                    FAQ
                  </Link>
                </li>
              </ul>
            </div>
            <div className="space-y-4">
              <h4 className="text-sm font-bold">Resources</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="/join-waitlist" className="text-muted-foreground hover:text-foreground transition-colors">
                    Join Waitlist
                  </Link>
                </li>
                <li>
                  <Link href="/about" className="text-muted-foreground hover:text-foreground transition-colors">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link href="/contact" className="text-muted-foreground hover:text-foreground transition-colors">
                    Contact
                  </Link>
                </li>
                <li>
                  <Link href="/login" className="text-muted-foreground hover:text-foreground transition-colors">
                    Login
                  </Link>
                </li>
              </ul>
            </div>
            <div className="space-y-4">
              <h4 className="text-sm font-bold">Company</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="/about" className="text-muted-foreground hover:text-foreground transition-colors">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link href="/contact" className="text-muted-foreground hover:text-foreground transition-colors">
                    Contact Us
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
                    Terms of Service
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="flex flex-col gap-4 sm:flex-row justify-between items-center border-t border-border/40 pt-8">
            <p className="text-xs text-muted-foreground">
              &copy; {new Date().getFullYear()} Relicon. All rights reserved.
            </p>
            <div className="flex gap-4">
              <Link href="#" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
                Privacy Policy
              </Link>
              <Link href="#" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
                Terms of Service
              </Link>
              <Link href="#" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
                Cookie Policy
              </Link>
            </div>
          </div>
        </div>
      </footer>
      <ScrollToTop />
    </div>
  )
}
