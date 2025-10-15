"use client"

import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Image from "next/image"

interface ProfileModalProps {
  isOpen: boolean
  onClose: () => void
}

export function ProfileModal({ isOpen, onClose }: ProfileModalProps) {
  if (!isOpen) return null

  return (
    <>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60]" onClick={onClose} />

      <div className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-[#0d0d0d] border border-[#2a2a2a] rounded-xl shadow-2xl z-[70]">
        <div className="flex items-center justify-between p-6 border-b border-[#2a2a2a]">
          <h2 className="text-lg font-semibold text-gray-200">Profile & Business Info</h2>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 text-gray-400 hover:text-gray-200">
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="p-6 space-y-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full overflow-hidden relative bg-[#161616]">
              <Image src="/professional-business-person.png" alt="Profile" fill className="object-cover" />
            </div>
            <Button
              variant="outline"
              size="sm"
              className="text-gray-300 border-[#2a2a2a] hover:bg-[#161616] bg-transparent"
            >
              Change Photo
            </Button>
          </div>

          <div className="space-y-4">
            <h3 className="text-sm font-medium text-gray-200">Personal Information</h3>
            <div className="space-y-3">
              <div>
                <Label className="text-sm text-gray-400">Full Name</Label>
                <Input defaultValue="Sarah Mitchell" className="mt-1.5 bg-[#161616] border-[#2a2a2a] text-gray-200" />
              </div>
              <div>
                <Label className="text-sm text-gray-400">Email</Label>
                <Input
                  defaultValue="sarah.mitchell@relicon.ai"
                  type="email"
                  className="mt-1.5 bg-[#161616] border-[#2a2a2a] text-gray-200"
                />
              </div>
              <div>
                <Label className="text-sm text-gray-400">Role</Label>
                <Input
                  defaultValue="Marketing Director"
                  className="mt-1.5 bg-[#161616] border-[#2a2a2a] text-gray-200"
                />
              </div>
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t border-[#2a2a2a]">
            <h3 className="text-sm font-medium text-gray-200">Business Information</h3>
            <div className="space-y-3">
              <div>
                <Label className="text-sm text-gray-400">Company Name</Label>
                <Input
                  defaultValue="TechFlow Solutions Inc."
                  className="mt-1.5 bg-[#161616] border-[#2a2a2a] text-gray-200"
                />
              </div>
              <div>
                <Label className="text-sm text-gray-400">Industry</Label>
                <Input
                  defaultValue="SaaS & Technology"
                  className="mt-1.5 bg-[#161616] border-[#2a2a2a] text-gray-200"
                />
              </div>
              <div>
                <Label className="text-sm text-gray-400">Monthly Ad Spend</Label>
                <Input defaultValue="$45,000" className="mt-1.5 bg-[#161616] border-[#2a2a2a] text-gray-200" />
              </div>
              <div>
                <Label className="text-sm text-gray-400">Team Size</Label>
                <Input defaultValue="12 members" className="mt-1.5 bg-[#161616] border-[#2a2a2a] text-gray-200" />
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 p-6 border-t border-[#2a2a2a]">
          <Button variant="ghost" onClick={onClose} className="text-gray-400 hover:text-gray-200">
            Cancel
          </Button>
          <Button onClick={onClose} className="bg-[#7c3aed] hover:bg-[#6d28d9] text-white">
            Save Changes
          </Button>
        </div>
      </div>
    </>
  )
}
