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
import { Train, Plus, Search, Edit, Trash2, MapPin, Activity } from "lucide-react"

interface TrainData {
  id: string
  model: string
  capacity: number
  status: "active" | "maintenance" | "inactive"
  currentLocation: string
  lastMaintenance: string
  nextMaintenance: string
  totalDistance: number
}

export function TrainManagement() {
  const [trains, setTrains] = useState<TrainData[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setTrains([
        {
          id: "BRC-001",
          model: "Shatabdi Express",
          capacity: 500,
          status: "active",
          currentLocation: "Platform 1",
          lastMaintenance: "2024-01-15",
          nextMaintenance: "2024-04-15",
          totalDistance: 145000,
        },
        {
          id: "BRC-002",
          model: "Gujarat Express",
          capacity: 800,
          status: "active",
          currentLocation: "Platform 2",
          lastMaintenance: "2024-02-01",
          nextMaintenance: "2024-03-01",
          totalDistance: 198000,
        },
        {
          id: "BRC-003",
          model: "Intercity Express",
          capacity: 600,
          status: "maintenance",
          currentLocation: "Baroda Depot",
          lastMaintenance: "2024-01-20",
          nextMaintenance: "2024-04-20",
          totalDistance: 87500,
        },
        {
          id: "BRC-004",
          model: "Rajdhani Express",
          capacity: 400,
          status: "active",
          currentLocation: "Platform 4",
          lastMaintenance: "2024-01-10",
          nextMaintenance: "2024-04-10",
          totalDistance: 256000,
        },
        {
          id: "BRC-005",
          model: "Local Passenger",
          capacity: 1200,
          status: "active",
          currentLocation: "Platform 3",
          lastMaintenance: "2024-02-05",
          nextMaintenance: "2024-03-05",
          totalDistance: 65000,
        },
      ])
      setLoading(false)
    }, 1000)
  }, [])

  const filteredTrains = trains.filter((train) => {
    const matchesSearch =
      train.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      train.model.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || train.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "default"
      case "maintenance":
        return "secondary"
      case "inactive":
        return "outline"
      default:
        return "outline"
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-balance">Baroda Station Train Management</h1>
          <p className="text-muted-foreground text-pretty">Manage trains operating at Baroda Railway Station</p>
        </div>
        <Dialog>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Train
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Train to Baroda Station</DialogTitle>
              <DialogDescription>Enter the details for the new train service</DialogDescription>
            </DialogHeader>
            <TrainForm />
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Trains</CardTitle>
            <Train className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{trains.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active</CardTitle>
            <Activity className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{trains.filter((t) => t.status === "active").length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Maintenance</CardTitle>
            <Activity className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{trains.filter((t) => t.status === "maintenance").length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Inactive</CardTitle>
            <Activity className="h-4 w-4 text-gray-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{trains.filter((t) => t.status === "inactive").length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>Baroda Station Train Fleet</CardTitle>
          <CardDescription>View and manage all trains operating at Baroda Railway Station</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search trains..."
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
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="maintenance">Maintenance</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Train ID</TableHead>
                <TableHead>Train Name</TableHead>
                <TableHead>Capacity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Current Location</TableHead>
                <TableHead>Next Maintenance</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8">
                    Loading trains...
                  </TableCell>
                </TableRow>
              ) : filteredTrains.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8">
                    No trains found
                  </TableCell>
                </TableRow>
              ) : (
                filteredTrains.map((train) => (
                  <TableRow key={train.id}>
                    <TableCell className="font-medium">{train.id}</TableCell>
                    <TableCell>{train.model}</TableCell>
                    <TableCell>{train.capacity} passengers</TableCell>
                    <TableCell>
                      <Badge variant={getStatusColor(train.status)}>{train.status}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {train.currentLocation}
                      </div>
                    </TableCell>
                    <TableCell>{train.nextMaintenance}</TableCell>
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

function TrainForm() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Train ID</label>
          <Input placeholder="BRC-006" />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Train Name</label>
          <Input placeholder="Express Train" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Capacity</label>
          <Input type="number" placeholder="500" />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Status</label>
          <Select>
            <SelectTrigger>
              <SelectValue placeholder="Select status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="maintenance">Maintenance</SelectItem>
              <SelectItem value="inactive">Inactive</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Current Location</label>
        <Input placeholder="Platform 1" />
      </div>
      <div className="flex justify-end gap-2 pt-4">
        <Button variant="outline">Cancel</Button>
        <Button>Add Train</Button>
      </div>
    </div>
  )
}
