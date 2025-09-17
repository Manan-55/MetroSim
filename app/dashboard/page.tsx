"use client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { AdminDashboard } from "@/components/dashboard/admin-dashboard"

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <AdminDashboard />
    </DashboardLayout>
  )
}
