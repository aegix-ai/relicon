"use client"

import { useState } from "react"
import Navbar from "@/components/navbar"
import HeroSection from "@/components/hero-section"
import WhyReelForge from "@/components/why-reelforge"
import HowItWorks from "@/components/how-it-works"
import VideoSamples from "@/components/video-samples"
import Pricing from "@/components/pricing"
import About from "@/components/about"
import Contact from "@/components/contact"
import Footer from "@/components/footer"
import Dashboard from "@/components/dashboard"
import ScrollToTop from "@/components/scroll-to-top"

export default function Home() {
  const [showDashboard, setShowDashboard] = useState(false)

  if (showDashboard) {
    return <Dashboard onBackToHome={() => setShowDashboard(false)} />
  }

  return (
    <main className="min-h-screen bg-white dark:bg-black transition-colors duration-300">
      <Navbar onEnterPanel={() => setShowDashboard(true)} />
      <HeroSection onEnterPanel={() => setShowDashboard(true)} />
      <WhyReelForge />
      <HowItWorks />
      <VideoSamples />
      <Pricing />
      <About />
      <Contact />
      <Footer />
      <ScrollToTop />
    </main>
  )
}
