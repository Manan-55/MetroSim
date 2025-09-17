"use client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { TrainManagement } from "@/components/trains/train-management"

export default function TrainsPage() {
  return (
    <DashboardLayout>
      <TrainManagement />
    </DashboardLayout>
  )
}
