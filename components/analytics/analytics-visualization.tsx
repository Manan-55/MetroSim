"use client"
import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts"
import { TrendingUp, TrendingDown, Activity, Download } from "lucide-react"

const performanceData = [
  { month: "Jan", onTime: 94, delayed: 6, cancelled: 0.5, passengers: 42000 },
  { month: "Feb", onTime: 92, delayed: 7, cancelled: 1, passengers: 45000 },
  { month: "Mar", onTime: 96, delayed: 3.5, cancelled: 0.5, passengers: 48000 },
  { month: "Apr", onTime: 89, delayed: 9, cancelled: 2, passengers: 44000 },
  { month: "May", onTime: 93, delayed: 6, cancelled: 1, passengers: 47000 },
  { month: "Jun", onTime: 95, delayed: 4, cancelled: 1, passengers: 49000 },
]

const passengerFlowData = [
  { hour: "06:00", passengers: 1200 },
  { hour: "07:00", passengers: 3500 },
  { hour: "08:00", passengers: 5200 },
  { hour: "09:00", passengers: 4800 },
  { hour: "10:00", passengers: 2800 },
  { hour: "11:00", passengers: 2200 },
  { hour: "12:00", passengers: 3100 },
  { hour: "13:00", passengers: 2900 },
  { hour: "14:00", passengers: 2600 },
  { hour: "15:00", passengers: 3200 },
  { hour: "16:00", passengers: 4100 },
  { hour: "17:00", passengers: 5800 },
  { hour: "18:00", passengers: 5400 },
  { hour: "19:00", passengers: 3900 },
  { hour: "20:00", passengers: 2100 },
]

const routePerformanceData = [
  { name: "Central Line", value: 35, performance: 94 },
  { name: "North Line", value: 28, performance: 91 },
  { name: "South Line", value: 22, performance: 96 },
  { name: "East Line", value: 15, performance: 88 },
]

const COLORS = ["#0891b2", "#60a5fa", "#3b82f6", "#1d4ed8"]

export function AnalyticsVisualization() {
  const [timeRange, setTimeRange] = useState("6months")
  const [selectedMetric, setSelectedMetric] = useState("performance")

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-balance">Analytics Dashboard</h1>
          <p className="text-muted-foreground text-pretty">Comprehensive operational insights and trends</p>
        </div>
        <div className="flex items-center gap-4">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1month">Last Month</SelectItem>
              <SelectItem value="3months">Last 3 Months</SelectItem>
              <SelectItem value="6months">Last 6 Months</SelectItem>
              <SelectItem value="1year">Last Year</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average On-Time</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">93.2%</div>
            <p className="text-xs text-green-600">+2.1% from last period</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily Passengers</CardTitle>
            <Activity className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">45.8K</div>
            <p className="text-xs text-blue-600">+8.3% from last period</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Energy Efficiency</CardTitle>
            <TrendingUp className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">87.5%</div>
            <p className="text-xs text-purple-600">+1.2% from last period</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Service Disruptions</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-red-600">-15% from last period</p>
          </CardContent>
        </Card>
      </div>

      {/* Performance Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Performance Trends</CardTitle>
            <CardDescription>On-time performance and delays over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="onTime" stroke="#0891b2" strokeWidth={2} name="On Time %" />
                <Line type="monotone" dataKey="delayed" stroke="#f59e0b" strokeWidth={2} name="Delayed %" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Passenger Volume</CardTitle>
            <CardDescription>Monthly passenger trends</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="passengers" stroke="#60a5fa" fill="#60a5fa" fillOpacity={0.3} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Daily Passenger Flow</CardTitle>
            <CardDescription>Hourly passenger distribution throughout the day</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={passengerFlowData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="passengers" fill="#0891b2" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Route Distribution</CardTitle>
            <CardDescription>Passenger distribution by route</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={routePerformanceData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {routePerformanceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Route Performance Table */}
      <Card>
        <CardHeader>
          <CardTitle>Route Performance Summary</CardTitle>
          <CardDescription>Detailed performance metrics by route</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {routePerformanceData.map((route, index) => (
              <div key={route.name} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS[index] }} />
                  <div>
                    <p className="font-medium">{route.name}</p>
                    <p className="text-sm text-muted-foreground">{route.value}% of total traffic</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm font-medium">{route.performance}% On-Time</p>
                    <Badge
                      variant={
                        route.performance >= 95 ? "default" : route.performance >= 90 ? "secondary" : "destructive"
                      }
                    >
                      {route.performance >= 95 ? "Excellent" : route.performance >= 90 ? "Good" : "Needs Improvement"}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
