"use client"

import { useState } from "react"
import { RoomStats } from "../status/RoomStats"
import { DeviceCard } from "../devices/DeviceCard"
import { MusicPlayer } from "../music/MusicPlayer"
import { LiveIndicator } from "../status/LiveIndicator"
import type { Device } from "@/types"
import Image from "next/image"

const initialDevices: Device[] = [
  {
    id: "1",
    name: "Living Lamp",
    type: "light",
    status: "on",
    room: "Living Room",
    usedSince: "06:20",
    image: "/images/devices/living-lamp.jpg",
  },
  {
    id: "2",
    name: "Homepod",
    type: "speaker",
    status: "on",
    room: "Living Room",
    usedSince: "08:30",
    image: "/images/devices/homepod.jpg",
  },
  {
    id: "3",
    name: "Air Humidifier",
    type: "humidifier",
    status: "on",
    room: "Living Room",
    usedSince: "10:00",
    value: 30,
    unit: "%",
    image: "/images/devices/air-humidifier.jpg",
  },
]

export function LivingRoom() {
  const [devices, setDevices] = useState(initialDevices)

  const handleDeviceStatusChange = (deviceId: string, status: "on" | "off") => {
    setDevices((prevDevices) => prevDevices.map((device) => (device.id === deviceId ? { ...device, status } : device)))
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      <div
        className="rounded-2xl sm:rounded-3xl overflow-hidden bg-gray-900 w-full h-56 sm:h-64 md:h-72 lg:h-80 xl:h-96"
        style={{ position: 'relative' }}
      >
        <Image
          src="/images/rooms/living-room.jpg"
          alt="Living Room"
          fill
          priority
          className="object-cover opacity-90"
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 66vw, 900px"
          style={{ objectFit: 'cover' }}
        />

        <LiveIndicator />

        <RoomStats temperature={20} humidity={30} power={250} efficiency={30} />

        <MusicPlayer
          songTitle="Oops! I did it again"
          artist="BRITNEY SPEARS"
          albumArt="/images/album-art/britney.jpg"
          currentTime="1:31"
          duration="3:02"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
        {devices.map((device) => (
          <DeviceCard key={device.id} device={device} onStatusChange={handleDeviceStatusChange} />
        ))}
      </div>
    </div>
  )
}
