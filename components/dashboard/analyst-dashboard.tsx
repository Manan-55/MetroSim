"use client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { BarChart3, TrendingUp, Brain, Activity, Clock, Users } from "lucide-react"

export function AnalystDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-balance">Analyst Dashboard</h1>
        <p className="text-muted-foreground text-pretty">Data insights and predictive analytics</p>
      </div>

      {/* Analytics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">On-Time Performance</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94.2%</div>
            <p className="text-xs text-muted-foreground">+2.1% from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily Passengers</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">45,231</div>
            <p className="text-xs text-muted-foreground">+8.3% from yesterday</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Efficiency Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">87.5</div>
            <p className="text-xs text-muted-foreground">Excellent performance</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">ML Accuracy</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">96.8%</div>
            <p className="text-xs text-muted-foreground">Prediction accuracy</p>
          </CardContent>
        </Card>
      </div>

      {/* Predictive Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Delay Predictions</CardTitle>
            <CardDescription>ML-powered delay forecasting for next 24 hours</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Morning Rush (7-9 AM)</span>
                <Badge variant="secondary">Low Risk</Badge>
              </div>
              <Progress value={25} className="h-2" />
              <div className="flex justify-between items-center">
                <span className="text-sm">Afternoon Peak (5-7 PM)</span>
                <Badge variant="destructive">High Risk</Badge>
              </div>
              <Progress value={85} className="h-2" />
              <div className="flex justify-between items-center">
                <span className="text-sm">Evening (8-10 PM)</span>
                <Badge variant="outline">Medium Risk</Badge>
              </div>
              <Progress value={45} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Passenger Flow Analysis</CardTitle>
            <CardDescription>Real-time passenger distribution</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { station: "Central Station", load: 85, trend: "up" },
                { station: "North Terminal", load: 62, trend: "stable" },
                { station: "South Junction", load: 78, trend: "down" },
                { station: "East Plaza", load: 45, trend: "up" },
              ].map((station) => (
                <div key={station.station} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{station.station}</p>
                    <p className="text-xs text-muted-foreground">{station.load}% capacity</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Progress value={station.load} className="w-20 h-2" />
                    <TrendingUp
                      className={`h-4 w-4 ${
                        station.trend === "up"
                          ? "text-red-500"
                          : station.trend === "down"
                            ? "text-green-500"
                            : "text-gray-500"
                      }`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Data Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Key Insights</CardTitle>
          <CardDescription>AI-generated operational insights</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <Brain className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <p className="text-sm font-medium">Peak Hour Optimization Opportunity</p>
                <p className="text-xs text-muted-foreground">
                  Adding 2 additional trains during 5-7 PM could reduce delays by 23%
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <BarChart3 className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <p className="text-sm font-medium">Maintenance Window Recommendation</p>
                <p className="text-xs text-muted-foreground">
                  Track A-3 showing wear patterns, schedule maintenance within 2 weeks
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Activity className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <p className="text-sm font-medium">Energy Efficiency Alert</p>
                <p className="text-xs text-muted-foreground">
                  Route optimization could save 15% energy consumption on North Line
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
