"use client"

import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  if (!isOpen) return null

  return (
    <>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60]" onClick={onClose} />

      <div className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-[#0d0d0d] border border-[#2a2a2a] rounded-xl shadow-2xl z-[70]">
        <div className="flex items-center justify-between p-6 border-b border-[#2a2a2a]">
          <h2 className="text-lg font-semibold text-gray-200">Settings</h2>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 text-gray-400 hover:text-gray-200">
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="p-6 space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-sm text-gray-200">Dark Mode</Label>
                <p className="text-xs text-gray-500">Always enabled for optimal viewing</p>
              </div>
              <Switch checked disabled />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-sm text-gray-200">Notifications</Label>
                <p className="text-xs text-gray-500">Get alerts for campaign updates</p>
              </div>
              <Switch />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-sm text-gray-200">Auto-refresh Data</Label>
                <p className="text-xs text-gray-500">Update metrics every 5 minutes</p>
              </div>
              <Switch defaultChecked />
            </div>
          </div>

          <div className="pt-4 border-t border-[#2a2a2a]">
            <h3 className="text-sm font-medium text-gray-200 mb-3">Connected Accounts</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 bg-[#161616] rounded-lg">
                <span className="text-sm text-gray-300">Google Ads</span>
                <span className="text-xs text-green-500">Connected</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-[#161616] rounded-lg">
                <span className="text-sm text-gray-300">Meta Ads</span>
                <span className="text-xs text-gray-500">Not connected</span>
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
