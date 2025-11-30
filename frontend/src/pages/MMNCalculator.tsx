import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  Legend
} from 'recharts';
import {
  AlertCircle,
  Users,
  Clock,
  Activity,
  Server,
  ArrowRight
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

// Types
interface MMNMetrics {
  utilization: number;
  erlang_c: number;
  mean_waiting_time: number;
  mean_response_time: number;
  mean_queue_length: number;
  mean_system_size: number;
}

const COLORS = ['#3b82f6', '#ef4444']; // Blue (Service), Red (Wait)

export const MMNCalculator = () => {
  // State
  const [lambda, setLambda] = useState(100);
  const [mu, setMu] = useState(12);
  const [N, setN] = useState(10);
  const [metrics, setMetrics] = useState<MMNMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Derived
  const rho = lambda / (N * mu);
  const isUnstable = rho >= 1;

  // Calculation Effect
  useEffect(() => {
    const calculate = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.post('/api/analytical/mmn', {
          arrival_rate: lambda,
          num_threads: N,
          service_rate: mu,
        });
        setMetrics(response.data.metrics);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Calculation failed');
      } finally {
        setLoading(false);
      }
    };

    // Debounce slightly to avoid rapid API calls on slider drag
    const timer = setTimeout(calculate, 100);
    return () => clearTimeout(timer);
  }, [lambda, mu, N]);

  // Animation variants
  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <div className="space-y-8 pb-10">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">M/M/N Calculator</h1>
        <p className="text-muted-foreground">
          Analyze multi-server queues with exponential inter-arrival and service times.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Controls Panel */}
        <Card className="lg:col-span-4 h-fit">
          <CardHeader>
            <CardTitle>Parameters</CardTitle>
            <CardDescription>Adjust system configuration</CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Lambda Slider */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <Label className="text-base font-medium">Arrival Rate (λ)</Label>
                <span className="text-sm font-mono bg-muted px-2 py-1 rounded">
                  {lambda} msg/s
                </span>
              </div>
              <Slider
                value={[lambda]}
                onValueChange={(v: number[]) => setLambda(v[0])}
                min={10}
                max={200}
                step={5}
                className="py-2"
              />
              <p className="text-xs text-muted-foreground">
                Rate of incoming requests per second
              </p>
            </div>

            {/* Mu Slider */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <Label className="text-base font-medium">Service Rate (μ)</Label>
                <span className="text-sm font-mono bg-muted px-2 py-1 rounded">
                  {mu} msg/s
                </span>
              </div>
              <Slider
                value={[mu]}
                onValueChange={(v: number[]) => setMu(v[0])}
                min={5}
                max={50}
                step={1}
                className="py-2"
              />
              <p className="text-xs text-muted-foreground">
                Processing capacity per single thread
              </p>
            </div>

            {/* N Slider */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <Label className="text-base font-medium">Threads (N)</Label>
                <span className="text-sm font-mono bg-muted px-2 py-1 rounded">
                  {N} threads
                </span>
              </div>
              <Slider
                value={[N]}
                onValueChange={(v: number[]) => setN(v[0])}
                min={1}
                max={30}
                step={1}
                className="py-2"
              />
              <p className="text-xs text-muted-foreground">
                Number of concurrent processing threads
              </p>
            </div>

            {/* Stability Alert */}
            {isUnstable && (
              <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
                <div className="flex items-center gap-2 font-semibold">
                  <AlertCircle className="h-4 w-4" />
                  System Unstable
                </div>
                <p className="mt-1 text-sm">
                  Utilization (ρ = {rho.toFixed(2)}) ≥ 1. Queue will grow infinitely.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results Panel */}
        <div className="lg:col-span-8 space-y-6">
          {metrics && !isUnstable ? (
            <motion.div
              variants={container}
              initial="hidden"
              animate="show"
              className="space-y-6"
            >
              {/* Key Metrics Grid */}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <motion.div variants={item}>
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Utilization</CardTitle>
                      <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className={cn(
                        "text-2xl font-bold",
                        metrics.utilization > 0.8 ? "text-orange-500" : "text-green-500"
                      )}>
                        {(metrics.utilization * 100).toFixed(1)}%
                      </div>
                      <p className="text-xs text-muted-foreground">
                        System load factor (ρ)
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>

                <motion.div variants={item}>
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Mean Wait</CardTitle>
                      <Clock className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {(metrics.mean_waiting_time * 1000).toFixed(1)} ms
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Avg time in queue (Wq)
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>

                <motion.div variants={item}>
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Queue Length</CardTitle>
                      <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {metrics.mean_queue_length.toFixed(2)}
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Avg items waiting (Lq)
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              </div>

              {/* Charts Section */}
              <div className="grid gap-6 md:grid-cols-2">
                {/* Response Time Breakdown */}
                <motion.div variants={item}>
                  <Card className="h-full">
                    <CardHeader>
                      <CardTitle>Response Time Breakdown</CardTitle>
                      <CardDescription>Service vs. Wait Time</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={[
                              { name: 'Service Time', value: 1 / mu },
                              { name: 'Wait Time', value: metrics.mean_waiting_time }
                            ]}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            <Cell fill={COLORS[0]} />
                            <Cell fill={COLORS[1]} />
                          </Pie>
                          <RechartsTooltip
                            formatter={(value: number) => `${(value * 1000).toFixed(1)} ms`}
                          />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </motion.div>

                {/* Detailed Stats */}
                <motion.div variants={item}>
                  <Card className="h-full">
                    <CardHeader>
                      <CardTitle>Detailed Statistics</CardTitle>
                      <CardDescription>Advanced metrics</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex justify-between items-center border-b pb-2">
                        <span className="text-sm font-medium">Erlang-C Probability</span>
                        <span className="font-mono">{(metrics.erlang_c * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between items-center border-b pb-2">
                        <span className="text-sm font-medium">Mean Response Time</span>
                        <span className="font-mono">{(metrics.mean_response_time * 1000).toFixed(1)} ms</span>
                      </div>
                      <div className="flex justify-between items-center border-b pb-2">
                        <span className="text-sm font-medium">Total System Size</span>
                        <span className="font-mono">{metrics.mean_system_size.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between items-center pt-2">
                        <span className="text-sm font-medium">Traffic Intensity (a)</span>
                        <span className="font-mono">{(lambda / mu).toFixed(2)} Erlangs</span>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              </div>
            </motion.div>
          ) : (
            <div className="flex h-full items-center justify-center p-8 text-muted-foreground">
              {isUnstable ? "Adjust parameters to stabilize system" : "Loading..."}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
