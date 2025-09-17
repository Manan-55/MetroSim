"use client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Train, MapPin, AlertCircle, CheckCircle, XCircle } from "lucide-react"

export function OperatorDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-balance">Operator Dashboard</h1>
        <p className="text-muted-foreground text-pretty">Real-time train operations and control</p>
      </div>

      {/* Operational Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Trains in Service</CardTitle>
            <Train className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">18</div>
            <p className="text-xs text-muted-foreground">6 delayed, 12 on time</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Routes</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8</div>
            <p className="text-xs text-muted-foreground">All routes operational</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Actions</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">5</div>
            <p className="text-xs text-muted-foreground">Require attention</p>
          </CardContent>
        </Card>
      </div>

      {/* Live Train Status */}
      <Card>
        <CardHeader>
          <CardTitle>Live Train Status</CardTitle>
          <CardDescription>Real-time monitoring of active trains</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { id: "T-001", route: "Central Line", status: "on-time", delay: 0, location: "Station A" },
              { id: "T-002", route: "North Line", status: "delayed", delay: 15, location: "Between B-C" },
              { id: "T-003", route: "South Line", status: "on-time", delay: 0, location: "Station D" },
              { id: "T-004", route: "East Line", status: "delayed", delay: 8, location: "Station E" },
            ].map((train) => (
              <div key={train.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <Train className="h-5 w-5 text-primary" />
                  <div>
                    <p className="font-medium">{train.id}</p>
                    <p className="text-sm text-muted-foreground">{train.route}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="text-sm font-medium">{train.location}</p>
                    {train.delay > 0 && <p className="text-xs text-red-600">+{train.delay} min delay</p>}
                  </div>
                  <Badge variant={train.status === "on-time" ? "default" : "destructive"}>
                    {train.status === "on-time" ? (
                      <CheckCircle className="h-3 w-3 mr-1" />
                    ) : (
                      <XCircle className="h-3 w-3 mr-1" />
                    )}
                    {train.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Control Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Emergency Controls</CardTitle>
            <CardDescription>Critical system controls</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="destructive" className="w-full">
              Emergency Stop All Trains
            </Button>
            <Button variant="outline" className="w-full bg-transparent">
              Activate Backup Systems
            </Button>
            <Button variant="outline" className="w-full bg-transparent">
              Contact Control Center
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Alerts</CardTitle>
            <CardDescription>System notifications and warnings</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium">Track maintenance scheduled</p>
                  <p className="text-xs text-muted-foreground">Track A-5, tomorrow 2:00 AM</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <AlertCircle className="h-4 w-4 text-red-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium">Signal malfunction detected</p>
                  <p className="text-xs text-muted-foreground">Junction B-7, requires inspection</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
