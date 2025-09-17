"use client"

import type React from "react"
import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Train, BarChart3, Settings, Users, Calendar, MapPin, Activity, Brain, Play, Menu, X } from "lucide-react"

interface NavItem {
  title: string
  href: string
  icon: React.ComponentType<{ className?: string }>
}

const navItems: NavItem[] = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: BarChart3,
  },
  {
    title: "Trains",
    href: "/trains",
    icon: Train,
  },
  {
    title: "Tracks",
    href: "/tracks",
    icon: MapPin,
  },
  {
    title: "Schedules",
    href: "/schedules",
    icon: Calendar,
  },
  {
    title: "Analytics",
    href: "/analytics",
    icon: Activity,
  },
  {
    title: "ML Predictions",
    href: "/predictions",
    icon: Brain,
  },
  {
    title: "Simulations",
    href: "/simulations",
    icon: Play,
  },
  {
    title: "Users",
    href: "/users",
    icon: Users,
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

  return (
    <div className={cn("flex flex-col h-full bg-sidebar border-r border-sidebar-border", collapsed ? "w-16" : "w-64")}>
      <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <Train className="h-6 w-6 text-primary" />
            <span className="font-semibold text-sidebar-foreground">TMS</span>
          </div>
        )}
        <Button variant="ghost" size="sm" onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? <Menu className="h-4 w-4" /> : <X className="h-4 w-4" />}
        </Button>
      </div>

      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href

            return (
              <Link key={item.href} href={item.href}>
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className={cn(
                    "w-full justify-start gap-3",
                    collapsed && "justify-center px-2",
                    isActive && "bg-sidebar-accent text-sidebar-accent-foreground",
                  )}
                >
                  <Icon className="h-4 w-4 flex-shrink-0" />
                  {!collapsed && <span>{item.title}</span>}
                </Button>
              </Link>
            )
          })}
        </nav>
      </ScrollArea>

      <div className="p-3 border-t border-sidebar-border">
        <div className="p-2 rounded-lg bg-sidebar-primary">
          <p className="text-sm font-medium text-sidebar-primary-foreground">Train Management System</p>
          <p className="text-xs text-sidebar-primary-foreground/70">Full Access Mode</p>
        </div>
      </div>
    </div>
  )
}
