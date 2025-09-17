"use client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { TrackManagement } from "@/components/tracks/track-management"

export default function TracksPage() {
  return (
    <DashboardLayout>
      <TrackManagement />
    </DashboardLayout>
  )
}
