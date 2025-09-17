"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { Play, Pause, Square, RotateCcw, Settings, Activity, Clock, Users, Zap } from "lucide-react"

interface SimulationState {
  status: "idle" | "running" | "paused" | "completed"
  progress: number
  timeElapsed: number
  scenario: string
  parameters: {
    trainCount: number
    passengerLoad: number
    weatherCondition: string
    timeOfDay: string
    speed: number
  }
  results: {
    onTimePerformance: number
    passengerSatisfaction: number
    energyEfficiency: number
    totalPassengers: number
  }
}

export function SimulationControls() {
  const [simulation, setSimulation] = useState<SimulationState>({
    status: "idle",
    progress: 0,
    timeElapsed: 0,
    scenario: "rush_hour",
    parameters: {
      trainCount: 12,
      passengerLoad: 75,
      weatherCondition: "clear",
      timeOfDay: "morning",
      speed: 1,
    },
    results: {
      onTimePerformance: 0,
      passengerSatisfaction: 0,
      energyEfficiency: 0,
      totalPassengers: 0,
    },
  })

  const [intervalId, setIntervalId] = useState<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (simulation.status === "running") {
      const id = setInterval(() => {
        setSimulation((prev) => {
          const newProgress = Math.min(prev.progress + prev.parameters.speed, 100)
          const newTimeElapsed = prev.timeElapsed + 1

          // Simulate results based on progress
          const results = {
            onTimePerformance: Math.min(85 + (newProgress / 100) * 10, 95),
            passengerSatisfaction: Math.min(80 + (newProgress / 100) * 15, 92),
            energyEfficiency: Math.min(70 + (newProgress / 100) * 20, 88),
            totalPassengers: Math.floor((newProgress / 100) * 45000),
          }

          return {
            ...prev,
            progress: newProgress,
            timeElapsed: newTimeElapsed,
            results,
            status: newProgress >= 100 ? "completed" : "running",
          }
        })
      }, 1000)
      setIntervalId(id)
    } else {
      if (intervalId) {
        clearInterval(intervalId)
        setIntervalId(null)
      }
    }

    return () => {
      if (intervalId) clearInterval(intervalId)
    }
  }, [simulation.status, simulation.parameters.speed])

  const startSimulation = () => {
    setSimulation((prev) => ({ ...prev, status: "running" }))
  }

  const pauseSimulation = () => {
    setSimulation((prev) => ({ ...prev, status: "paused" }))
  }

  const stopSimulation = () => {
    setSimulation((prev) => ({
      ...prev,
      status: "idle",
      progress: 0,
      timeElapsed: 0,
      results: {
        onTimePerformance: 0,
        passengerSatisfaction: 0,
        energyEfficiency: 0,
        totalPassengers: 0,
      },
    }))
  }

  const resetSimulation = () => {
    stopSimulation()
  }

  const updateParameter = (key: string, value: any) => {
    setSimulation((prev) => ({
      ...prev,
      parameters: { ...prev.parameters, [key]: value },
    }))
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running":
        return "default"
      case "paused":
        return "secondary"
      case "completed":
        return "outline"
      default:
        return "outline"
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-balance">Train Simulation</h1>
          <p className="text-muted-foreground text-pretty">Test scenarios and optimize operations</p>
        </div>
        <Badge variant={getStatusColor(simulation.status)} className="text-sm px-3 py-1">
          {simulation.status.toUpperCase()}
        </Badge>
      </div>

      {/* Simulation Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Simulation Controls</CardTitle>
              <CardDescription>Configure and run train operation simulations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Control Buttons */}
              <div className="flex gap-3">
                <Button
                  onClick={startSimulation}
                  disabled={simulation.status === "running" || simulation.status === "completed"}
                  className="flex-1"
                >
                  <Play className="h-4 w-4 mr-2" />
                  Start
                </Button>
                <Button
                  onClick={pauseSimulation}
                  disabled={simulation.status !== "running"}
                  variant="outline"
                  className="flex-1 bg-transparent"
                >
                  <Pause className="h-4 w-4 mr-2" />
                  Pause
                </Button>
                <Button
                  onClick={stopSimulation}
                  disabled={simulation.status === "idle"}
                  variant="outline"
                  className="flex-1 bg-transparent"
                >
                  <Square className="h-4 w-4 mr-2" />
                  Stop
                </Button>
                <Button onClick={resetSimulation} variant="outline">
                  <RotateCcw className="h-4 w-4" />
                </Button>
              </div>

              {/* Progress */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Simulation Progress</span>
                  <span>{simulation.progress.toFixed(1)}%</span>
                </div>
                <Progress value={simulation.progress} className="h-3" />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>
                    Time Elapsed: {Math.floor(simulation.timeElapsed / 60)}:
                    {(simulation.timeElapsed % 60).toString().padStart(2, "0")}
                  </span>
                  <span>
                    ETA:{" "}
                    {simulation.status === "running"
                      ? `${Math.ceil((100 - simulation.progress) / simulation.parameters.speed)}s`
                      : "-"}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Scenario Parameters */}
          <Card>
            <CardHeader>
              <CardTitle>Scenario Configuration</CardTitle>
              <CardDescription>Adjust simulation parameters</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Scenario Type</label>
                  <Select
                    value={simulation.scenario}
                    onValueChange={(value) => setSimulation((prev) => ({ ...prev, scenario: value }))}
                    disabled={simulation.status === "running"}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="rush_hour">Rush Hour</SelectItem>
                      <SelectItem value="normal_operations">Normal Operations</SelectItem>
                      <SelectItem value="maintenance_mode">Maintenance Mode</SelectItem>
                      <SelectItem value="emergency_scenario">Emergency Scenario</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Weather Condition</label>
                  <Select
                    value={simulation.parameters.weatherCondition}
                    onValueChange={(value) => updateParameter("weatherCondition", value)}
                    disabled={simulation.status === "running"}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="clear">Clear</SelectItem>
                      <SelectItem value="rain">Rain</SelectItem>
                      <SelectItem value="snow">Snow</SelectItem>
                      <SelectItem value="fog">Fog</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <label className="text-sm font-medium">Number of Trains</label>
                    <span className="text-sm text-muted-foreground">{simulation.parameters.trainCount}</span>
                  </div>
                  <Slider
                    value={[simulation.parameters.trainCount]}
                    onValueChange={([value]) => updateParameter("trainCount", value)}
                    max={20}
                    min={5}
                    step={1}
                    disabled={simulation.status === "running"}
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <label className="text-sm font-medium">Passenger Load (%)</label>
                    <span className="text-sm text-muted-foreground">{simulation.parameters.passengerLoad}%</span>
                  </div>
                  <Slider
                    value={[simulation.parameters.passengerLoad]}
                    onValueChange={([value]) => updateParameter("passengerLoad", value)}
                    max={100}
                    min={20}
                    step={5}
                    disabled={simulation.status === "running"}
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <label className="text-sm font-medium">Simulation Speed</label>
                    <span className="text-sm text-muted-foreground">{simulation.parameters.speed}x</span>
                  </div>
                  <Slider
                    value={[simulation.parameters.speed]}
                    onValueChange={([value]) => updateParameter("speed", value)}
                    max={5}
                    min={1}
                    step={1}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Real-time Results */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Live Results</CardTitle>
              <CardDescription>Real-time simulation metrics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-primary" />
                    <span className="text-sm">On-Time Performance</span>
                  </div>
                  <span className="text-sm font-medium">{simulation.results.onTimePerformance.toFixed(1)}%</span>
                </div>
                <Progress value={simulation.results.onTimePerformance} className="h-2" />

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-primary" />
                    <span className="text-sm">Passenger Satisfaction</span>
                  </div>
                  <span className="text-sm font-medium">{simulation.results.passengerSatisfaction.toFixed(1)}%</span>
                </div>
                <Progress value={simulation.results.passengerSatisfaction} className="h-2" />

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-primary" />
                    <span className="text-sm">Energy Efficiency</span>
                  </div>
                  <span className="text-sm font-medium">{simulation.results.energyEfficiency.toFixed(1)}%</span>
                </div>
                <Progress value={simulation.results.energyEfficiency} className="h-2" />

                <div className="flex items-center justify-between pt-2 border-t">
                  <span className="text-sm">Total Passengers</span>
                  <span className="text-sm font-medium">{simulation.results.totalPassengers.toLocaleString()}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
              <CardDescription>Current simulation state</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-3">
                <Activity className="h-4 w-4 text-green-600" />
                <div>
                  <p className="text-sm font-medium">Simulation Engine</p>
                  <p className="text-xs text-muted-foreground">Running optimally</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Settings className="h-4 w-4 text-blue-600" />
                <div>
                  <p className="text-sm font-medium">Parameters</p>
                  <p className="text-xs text-muted-foreground">
                    {simulation.parameters.trainCount} trains, {simulation.parameters.passengerLoad}% load
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Clock className="h-4 w-4 text-purple-600" />
                <div>
                  <p className="text-sm font-medium">Scenario</p>
                  <p className="text-xs text-muted-foreground">{simulation.scenario.replace("_", " ")}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Historical Results */}
      {simulation.status === "completed" && (
        <Card>
          <CardHeader>
            <CardTitle>Simulation Complete</CardTitle>
            <CardDescription>Final results and recommendations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-muted rounded-lg">
                <div className="text-2xl font-bold text-primary">
                  {simulation.results.onTimePerformance.toFixed(1)}%
                </div>
                <div className="text-sm text-muted-foreground">On-Time Performance</div>
              </div>
              <div className="text-center p-4 bg-muted rounded-lg">
                <div className="text-2xl font-bold text-primary">
                  {simulation.results.passengerSatisfaction.toFixed(1)}%
                </div>
                <div className="text-sm text-muted-foreground">Passenger Satisfaction</div>
              </div>
              <div className="text-center p-4 bg-muted rounded-lg">
                <div className="text-2xl font-bold text-primary">{simulation.results.energyEfficiency.toFixed(1)}%</div>
                <div className="text-sm text-muted-foreground">Energy Efficiency</div>
              </div>
              <div className="text-center p-4 bg-muted rounded-lg">
                <div className="text-2xl font-bold text-primary">
                  {simulation.results.totalPassengers.toLocaleString()}
                </div>
                <div className="text-sm text-muted-foreground">Total Passengers</div>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium">Recommendations:</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li className="flex items-center gap-2">
                  <div className="w-1 h-1 bg-primary rounded-full" />
                  Consider adding 2 more trains during peak hours to improve on-time performance
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1 h-1 bg-primary rounded-full" />
                  Implement dynamic scheduling to optimize passenger satisfaction
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1 h-1 bg-primary rounded-full" />
                  Energy efficiency can be improved by 5% with regenerative braking
                </li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
