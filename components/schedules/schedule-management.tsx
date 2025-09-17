"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Calendar, Plus, Search, Edit, Trash2, Clock, MapPin, Train } from "lucide-react"

interface ScheduleData {
  id: string
  trainId: string
  route: string
  departureTime: string
  arrivalTime: string
  status: "scheduled" | "active" | "delayed" | "cancelled"
  delay: number
  passengers: number
  stops: string[]
}

export function ScheduleManagement() {
  const [schedules, setSchedules] = useState<ScheduleData[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setSchedules([
        {
          id: "SCH-001",
          trainId: "T-001",
          route: "Central Line",
          departureTime: "08:00",
          arrivalTime: "09:30",
          status: "active",
          delay: 0,
          passengers: 245,
          stops: ["Central Station", "North Plaza", "East Junction"],
        },
        {
          id: "SCH-002",
          trainId: "T-002",
          route: "North Line",
          departureTime: "08:15",
          arrivalTime: "09:45",
          status: "delayed",
          delay: 12,
          passengers: 189,
          stops: ["North Terminal", "City Center", "West Gate"],
        },
        {
          id: "SCH-003",
          trainId: "T-003",
          route: "South Line",
          departureTime: "08:30",
          arrivalTime: "10:15",
          status: "scheduled",
          delay: 0,
          passengers: 0,
          stops: ["South Station", "Harbor View", "Industrial Park"],
        },
        {
          id: "SCH-004",
          trainId: "T-004",
          route: "East Line",
          departureTime: "09:00",
          arrivalTime: "10:30",
          status: "cancelled",
          delay: 0,
          passengers: 0,
          stops: ["East Terminal", "Business District"],
        },
      ])
      setLoading(false)
    }, 1000)
  }, [])

  const filteredSchedules = schedules.filter((schedule) => {
    const matchesSearch =
      schedule.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      schedule.trainId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      schedule.route.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || schedule.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case "scheduled":
        return "outline"
      case "active":
        return "default"
      case "delayed":
        return "secondary"
      case "cancelled":
        return "destructive"
      default:
        return "outline"
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-balance">Schedule Management</h1>
          <p className="text-muted-foreground text-pretty">Create and manage train schedules</p>
        </div>
        <Dialog>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Schedule
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Schedule</DialogTitle>
              <DialogDescription>Set up a new train schedule</DialogDescription>
            </DialogHeader>
            <ScheduleForm />
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Schedules</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{schedules.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active</CardTitle>
            <Train className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{schedules.filter((s) => s.status === "active").length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Delayed</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{schedules.filter((s) => s.status === "delayed").length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">On-Time Rate</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(
                (schedules.filter((s) => s.status === "active" && s.delay === 0).length / schedules.length) * 100,
              )}
              %
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Schedule List */}
      <Card>
        <CardHeader>
          <CardTitle>Today's Schedules</CardTitle>
          <CardDescription>View and manage all scheduled trains</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search schedules..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="scheduled">Scheduled</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="delayed">Delayed</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Schedule ID</TableHead>
                <TableHead>Train</TableHead>
                <TableHead>Route</TableHead>
                <TableHead>Departure</TableHead>
                <TableHead>Arrival</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Passengers</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8">
                    Loading schedules...
                  </TableCell>
                </TableRow>
              ) : filteredSchedules.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8">
                    No schedules found
                  </TableCell>
                </TableRow>
              ) : (
                filteredSchedules.map((schedule) => (
                  <TableRow key={schedule.id}>
                    <TableCell className="font-medium">{schedule.id}</TableCell>
                    <TableCell>{schedule.trainId}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {schedule.route}
                      </div>
                    </TableCell>
                    <TableCell>{schedule.departureTime}</TableCell>
                    <TableCell>
                      {schedule.arrivalTime}
                      {schedule.delay > 0 && <div className="text-xs text-red-600">+{schedule.delay}min</div>}
                    </TableCell>
                    <TableCell>
                      <Badge variant={getStatusColor(schedule.status)}>{schedule.status}</Badge>
                    </TableCell>
                    <TableCell>{schedule.passengers > 0 ? schedule.passengers : "-"}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

function ScheduleForm() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Train</label>
          <Select>
            <SelectTrigger>
              <SelectValue placeholder="Select train" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="T-001">T-001 - Express 2000</SelectItem>
              <SelectItem value="T-002">T-002 - Metro Plus</SelectItem>
              <SelectItem value="T-003">T-003 - City Runner</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Route</label>
          <Select>
            <SelectTrigger>
              <SelectValue placeholder="Select route" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="central">Central Line</SelectItem>
              <SelectItem value="north">North Line</SelectItem>
              <SelectItem value="south">South Line</SelectItem>
              <SelectItem value="east">East Line</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Departure Time</label>
          <Input type="time" />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Arrival Time</label>
          <Input type="time" />
        </div>
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Date</label>
        <Input type="date" />
      </div>
      <div className="flex justify-end gap-2 pt-4">
        <Button variant="outline">Cancel</Button>
        <Button>Create Schedule</Button>
      </div>
    </div>
  )
}
