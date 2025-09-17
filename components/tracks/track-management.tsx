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
import { Progress } from "@/components/ui/progress"
import { MapPin, Plus, Search, Edit, Trash2, AlertTriangle, CheckCircle, Activity } from "lucide-react"

interface TrackData {
  id: string
  name: string
  length: number
  status: "operational" | "maintenance" | "closed"
  condition: number
  lastInspection: string
  nextMaintenance: string
  stations: string[]
  maxSpeed: number
}

export function TrackManagement() {
  const [tracks, setTracks] = useState<TrackData[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setTracks([
        {
          id: "A-1",
          name: "Central Line",
          length: 25.5,
          status: "operational",
          condition: 85,
          lastInspection: "2024-02-01",
          nextMaintenance: "2024-05-01",
          stations: ["Central Station", "North Plaza", "East Junction"],
          maxSpeed: 80,
        },
        {
          id: "A-2",
          name: "North Line",
          length: 18.2,
          status: "maintenance",
          condition: 65,
          lastInspection: "2024-01-15",
          nextMaintenance: "2024-03-15",
          stations: ["North Terminal", "City Center", "West Gate"],
          maxSpeed: 60,
        },
        {
          id: "A-3",
          name: "South Line",
          length: 32.1,
          status: "operational",
          condition: 92,
          lastInspection: "2024-02-10",
          nextMaintenance: "2024-06-10",
          stations: ["South Station", "Harbor View", "Industrial Park"],
          maxSpeed: 100,
        },
        {
          id: "A-4",
          name: "East Line",
          length: 15.8,
          status: "closed",
          condition: 45,
          lastInspection: "2024-01-20",
          nextMaintenance: "2024-02-20",
          stations: ["East Terminal", "Business District"],
          maxSpeed: 70,
        },
      ])
      setLoading(false)
    }, 1000)
  }, [])

  const filteredTracks = tracks.filter((track) => {
    const matchesSearch =
      track.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      track.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || track.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case "operational":
        return "default"
      case "maintenance":
        return "secondary"
      case "closed":
        return "destructive"
      default:
        return "outline"
    }
  }

  const getConditionColor = (condition: number) => {
    if (condition >= 80) return "text-green-600"
    if (condition >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-balance">Track Management</h1>
          <p className="text-muted-foreground text-pretty">Monitor and maintain railway infrastructure</p>
        </div>
        <Dialog>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Track
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Track</DialogTitle>
              <DialogDescription>Enter the details for the new track</DialogDescription>
            </DialogHeader>
            <TrackForm />
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tracks</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tracks.length}</div>
            <p className="text-xs text-muted-foreground">
              {tracks.reduce((sum, track) => sum + track.length, 0).toFixed(1)} km total
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Operational</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tracks.filter((t) => t.status === "operational").length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Under Maintenance</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tracks.filter((t) => t.status === "maintenance").length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Condition</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(tracks.reduce((sum, track) => sum + track.condition, 0) / tracks.length)}%
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Track Status Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Track Infrastructure</CardTitle>
          <CardDescription>Monitor track conditions and maintenance schedules</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search tracks..."
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
                <SelectItem value="operational">Operational</SelectItem>
                <SelectItem value="maintenance">Maintenance</SelectItem>
                <SelectItem value="closed">Closed</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Track ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Length</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Condition</TableHead>
                <TableHead>Stations</TableHead>
                <TableHead>Next Maintenance</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8">
                    Loading tracks...
                  </TableCell>
                </TableRow>
              ) : filteredTracks.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8">
                    No tracks found
                  </TableCell>
                </TableRow>
              ) : (
                filteredTracks.map((track) => (
                  <TableRow key={track.id}>
                    <TableCell className="font-medium">{track.id}</TableCell>
                    <TableCell>{track.name}</TableCell>
                    <TableCell>{track.length} km</TableCell>
                    <TableCell>
                      <Badge variant={getStatusColor(track.status)}>{track.status}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className={`text-sm font-medium ${getConditionColor(track.condition)}`}>
                            {track.condition}%
                          </span>
                        </div>
                        <Progress value={track.condition} className="h-1" />
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">{track.stations.length} stations</div>
                    </TableCell>
                    <TableCell>{track.nextMaintenance}</TableCell>
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

function TrackForm() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Track ID</label>
          <Input placeholder="A-5" />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Name</label>
          <Input placeholder="West Line" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Length (km)</label>
          <Input type="number" placeholder="20.5" />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Max Speed (km/h)</label>
          <Input type="number" placeholder="80" />
        </div>
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Status</label>
        <Select>
          <SelectTrigger>
            <SelectValue placeholder="Select status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="operational">Operational</SelectItem>
            <SelectItem value="maintenance">Maintenance</SelectItem>
            <SelectItem value="closed">Closed</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="flex justify-end gap-2 pt-4">
        <Button variant="outline">Cancel</Button>
        <Button>Add Track</Button>
      </div>
    </div>
  )
}
