"use client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { SimulationControls } from "@/components/simulations/simulation-controls"

export default function SimulationsPage() {
  return (
    <DashboardLayout>
      <SimulationControls />
    </DashboardLayout>
  )
}
