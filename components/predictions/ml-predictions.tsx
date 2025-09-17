"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Brain, TrendingUp, AlertTriangle, Clock, Activity, RefreshCw } from "lucide-react"

interface PredictionData {
  id: string
  type: "delay" | "maintenance" | "passenger_flow" | "energy"
  target: string
  prediction: string
  confidence: number
  timeframe: string
  impact: "low" | "medium" | "high"
  recommendations: string[]
}

export function MLPredictions() {
  const [predictions, setPredictions] = useState<PredictionData[]>([])
  const [selectedType, setSelectedType] = useState<string>("all")
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  useEffect(() => {
    loadPredictions()
  }, [])

  const loadPredictions = () => {
    setLoading(true)
    // Simulate API call
    setTimeout(() => {
      setPredictions([
        {
          id: "PRED-001",
          type: "delay",
          target: "Central Line",
          prediction: "15-minute delay expected during evening rush",
          confidence: 87,
          timeframe: "5:00 PM - 7:00 PM",
          impact: "high",
          recommendations: ["Deploy additional trains", "Notify passengers in advance", "Prepare alternative routes"],
        },
        {
          id: "PRED-002",
          type: "maintenance",
          target: "Track A-3",
          prediction: "Maintenance required within 2 weeks",
          confidence: 94,
          timeframe: "Next 14 days",
          impact: "medium",
          recommendations: [
            "Schedule maintenance window",
            "Prepare track closure notices",
            "Arrange alternative services",
          ],
        },
        {
          id: "PRED-003",
          type: "passenger_flow",
          target: "North Terminal",
          prediction: "Peak passenger load at 8:30 AM",
          confidence: 92,
          timeframe: "Tomorrow morning",
          impact: "medium",
          recommendations: ["Increase staff at station", "Monitor crowd levels", "Prepare crowd control measures"],
        },
        {
          id: "PRED-004",
          type: "energy",
          target: "South Line",
          prediction: "20% energy savings possible with route optimization",
          confidence: 78,
          timeframe: "Ongoing",
          impact: "low",
          recommendations: ["Implement speed optimization", "Review braking patterns", "Consider regenerative braking"],
        },
      ])
      setLastUpdate(new Date())
      setLoading(false)
    }, 1000)
  }

  const filteredPredictions = predictions.filter((prediction) => {
    return selectedType === "all" || prediction.type === selectedType
  })

  const getTypeColor = (type: string) => {
    switch (type) {
      case "delay":
        return "destructive"
      case "maintenance":
        return "secondary"
      case "passenger_flow":
        return "default"
      case "energy":
        return "outline"
      default:
        return "outline"
    }
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case "high":
        return "text-red-600"
      case "medium":
        return "text-yellow-600"
      case "low":
        return "text-green-600"
      default:
        return "text-gray-600"
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return "text-green-600"
    if (confidence >= 70) return "text-yellow-600"
    return "text-red-600"
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-balance">ML Predictions</h1>
          <p className="text-muted-foreground text-pretty">AI-powered operational insights and forecasts</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-muted-foreground">Last updated: {lastUpdate.toLocaleTimeString()}</div>
          <Button onClick={loadPredictions} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Model Performance */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Model Accuracy</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94.2%</div>
            <p className="text-xs text-muted-foreground">Average across all models</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Predictions</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{predictions.length}</div>
            <p className="text-xs text-muted-foreground">Real-time forecasts</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High Priority</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{predictions.filter((p) => p.impact === "high").length}</div>
            <p className="text-xs text-muted-foreground">Require immediate attention</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Processing Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1.2s</div>
            <p className="text-xs text-muted-foreground">Average prediction time</p>
          </CardContent>
        </Card>
      </div>

      {/* Prediction Filters */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Prediction Dashboard</CardTitle>
              <CardDescription>AI-generated insights and recommendations</CardDescription>
            </div>
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Predictions</SelectItem>
                <SelectItem value="delay">Delay Predictions</SelectItem>
                <SelectItem value="maintenance">Maintenance</SelectItem>
                <SelectItem value="passenger_flow">Passenger Flow</SelectItem>
                <SelectItem value="energy">Energy Optimization</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading predictions...</div>
          ) : (
            <div className="space-y-6">
              {filteredPredictions.map((prediction) => (
                <Card key={prediction.id} className="border-l-4 border-l-primary">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <Badge variant={getTypeColor(prediction.type)}>{prediction.type.replace("_", " ")}</Badge>
                          <span className="text-sm font-medium">{prediction.target}</span>
                        </div>
                        <h3 className="text-lg font-semibold text-balance">{prediction.prediction}</h3>
                      </div>
                      <div className="text-right space-y-1">
                        <div className={`text-sm font-medium ${getImpactColor(prediction.impact)}`}>
                          {prediction.impact.toUpperCase()} IMPACT
                        </div>
                        <div className="text-xs text-muted-foreground">{prediction.timeframe}</div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Confidence Level</span>
                        <span className={`text-sm font-bold ${getConfidenceColor(prediction.confidence)}`}>
                          {prediction.confidence}%
                        </span>
                      </div>
                      <Progress value={prediction.confidence} className="h-2" />
                    </div>

                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">Recommended Actions:</h4>
                      <ul className="space-y-1">
                        {prediction.recommendations.map((rec, index) => (
                          <li key={index} className="text-sm text-muted-foreground flex items-center gap-2">
                            <div className="w-1 h-1 bg-primary rounded-full" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Model Performance Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Model Performance Metrics</CardTitle>
            <CardDescription>Real-time model accuracy and performance</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Delay Prediction Model</span>
                <span className="text-sm font-medium">96.8%</span>
              </div>
              <Progress value={96.8} className="h-2" />

              <div className="flex justify-between items-center">
                <span className="text-sm">Maintenance Prediction</span>
                <span className="text-sm font-medium">94.2%</span>
              </div>
              <Progress value={94.2} className="h-2" />

              <div className="flex justify-between items-center">
                <span className="text-sm">Passenger Flow Model</span>
                <span className="text-sm font-medium">91.5%</span>
              </div>
              <Progress value={91.5} className="h-2" />

              <div className="flex justify-between items-center">
                <span className="text-sm">Energy Optimization</span>
                <span className="text-sm font-medium">89.3%</span>
              </div>
              <Progress value={89.3} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Prediction Trends</CardTitle>
            <CardDescription>Historical accuracy and improvement trends</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <TrendingUp className="h-5 w-5 text-green-600" />
                <div>
                  <p className="text-sm font-medium">Accuracy Improvement</p>
                  <p className="text-xs text-muted-foreground">+3.2% over last month</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Brain className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-sm font-medium">Model Updates</p>
                  <p className="text-xs text-muted-foreground">Last retrained 2 days ago</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Activity className="h-5 w-5 text-purple-600" />
                <div>
                  <p className="text-sm font-medium">Data Quality</p>
                  <p className="text-xs text-muted-foreground">98.7% clean data rate</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
