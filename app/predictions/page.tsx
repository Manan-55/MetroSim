"use client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { MLPredictions } from "@/components/predictions/ml-predictions"

export default function PredictionsPage() {
  return (
    <DashboardLayout>
      <MLPredictions />
    </DashboardLayout>
  )
}
