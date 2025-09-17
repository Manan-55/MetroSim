"use client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { AnalyticsVisualization } from "@/components/analytics/analytics-visualization"

export default function AnalyticsPage() {
  return (
    <DashboardLayout>
      <AnalyticsVisualization />
    </DashboardLayout>
  )
}
