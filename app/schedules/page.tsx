"use client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ScheduleManagement } from "@/components/schedules/schedule-management"

export default function SchedulesPage() {
  return (
    <DashboardLayout>
      <ScheduleManagement />
    </DashboardLayout>
  )
}
