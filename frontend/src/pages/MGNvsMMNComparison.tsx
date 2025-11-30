import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';
import {
  ArrowRight,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';
import { cn } from '@/lib/utils';

// Types
interface ComparisonMetrics {
  mmn: {
    mean_waiting_time: number;
    mean_response_time: number;
    utilization: number;
    erlang_c: number;
  };
  mgn: {
    mean_waiting_time: number;
    mean_response_time: number;
    cv_squared: number;
    p99_response_time_heavy_tail: number;
  };
}

export const MGNvsMMNComparison = () => {
  // State
  const [lambda, setLambda] = useState(100);
  const [mu, setMu] = useState(12);
  const [N, setN] = useState(10);
  const [alpha, setAlpha] = useState(2.5);

  const [metrics, setMetrics] = useState<ComparisonMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Derived
  const rho = lambda / (N * mu);
  const isUnstable = rho >= 1;
  const cv2 = alpha > 2 ? 1 / (alpha * (alpha - 2)) : 10;

  // Calculation
  const calculateComparison = async () => {
    setLoading(true);
    setError(null);
    try {
      // M/M/N
      const mmnResponse = await axios.post('/api/analytical/mmn', {
        arrival_rate: lambda,
        num_threads: N,
        service_rate: mu,
      });

      // M/G/N
      const meanService = 1 / mu;
      const variance = cv2 * meanService * meanService;
      const mgnResponse = await axios.post('/api/analytical/mgn', {
        arrival_rate: lambda,
        num_threads: N,
        mean_service: meanService,
        variance_service: variance,
      });

      setMetrics({
        mmn: mmnResponse.data.metrics,
        mgn: mgnResponse.data.metrics,
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(calculateComparison, 100);
    return () => clearTimeout(timer);
  }, [lambda, mu, N, alpha]);

  // Animation
  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  // Chart Data
  const chartData = metrics ? [
    {
      name: 'Mean Wait (Wq)',
      MMN: metrics.mmn.mean_waiting_time * 1000,
      MGN: metrics.mgn.mean_waiting_time * 1000,
    },
    {
      name: 'Response Time (R)',
      MMN: metrics.mmn.mean_response_time * 1000,
      MGN: metrics.mgn.mean_response_time * 1000,
    }
  ] : [];

  const getPercentChange = (current: number, baseline: number) => {
    const diff = ((current - baseline) / baseline) * 100;
    return diff;
  };

  return (
    <div className="space-y-8 pb-10">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Model Comparison</h1>
        <p className="text-muted-foreground">
          Compare the standard M/M/N model against the heavy-tailed M/G/N model.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Controls */}
        <Card className="lg:col-span-4 h-fit">
          <CardHeader>
            <CardTitle>Scenario Setup</CardTitle>
            <CardDescription>Adjust parameters for both models</CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <Label>Arrival Rate (λ)</Label>
                <span className="font-mono">{lambda}</span>
              </div>
              <Slider value={[lambda]} onValueChange={(v: number[]) => setLambda(v[0])} min={10} max={200} step={5} />

              <div className="flex justify-between text-sm">
                <Label>Service Rate (μ)</Label>
                <span className="font-mono">{mu}</span>
              </div>
              <Slider value={[mu]} onValueChange={(v: number[]) => setMu(v[0])} min={5} max={50} step={1} />

              <div className="flex justify-between text-sm">
                <Label>Threads (N)</Label>
                <span className="font-mono">{N}</span>
              </div>
              <Slider value={[N]} onValueChange={(v: number[]) => setN(v[0])} min={1} max={30} step={1} />

              <div className="pt-4 border-t space-y-4">
                <div className="flex justify-between items-center">
                  <Label>Pareto Shape (α)</Label>
                  <span className={cn(
                    "text-sm font-mono px-2 py-1 rounded",
                    alpha <= 2.1 ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" : "bg-muted"
                  )}>
                    α = {alpha}
                  </span>
                </div>
                <Slider value={[alpha]} onValueChange={(v: number[]) => setAlpha(v[0])} min={2.1} max={5.0} step={0.1} />
                <p className="text-xs text-muted-foreground">
                  Affects M/G/N only. Lower α = Heavier tail.
                </p>
              </div>
            </div>

            {isUnstable && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Unstable System</AlertTitle>
                <AlertDescription>
                  Utilization (ρ = {rho.toFixed(2)}) ≥ 1.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Results */}
        <div className="lg:col-span-8 space-y-6">
          {metrics && !isUnstable ? (
            <motion.div
              variants={container}
              initial="hidden"
              animate="show"
              className="space-y-6"
            >
              {/* Comparison Chart */}
              <motion.div variants={item}>
                <Card>
                  <CardHeader>
                    <CardTitle>Performance Gap</CardTitle>
                    <CardDescription>M/M/N (Baseline) vs M/G/N (Heavy-Tailed)</CardDescription>
                  </CardHeader>
                  <CardContent className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                        <XAxis dataKey="name" />
                        <YAxis label={{ value: 'Time (ms)', angle: -90, position: 'insideLeft' }} />
                        <RechartsTooltip
                          formatter={(value: number) => `${value.toFixed(1)} ms`}
                          cursor={{ fill: 'transparent' }}
                        />
                        <Legend />
                        <Bar name="M/M/N (Exponential)" dataKey="MMN" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                        <Bar name="M/G/N (Pareto)" dataKey="MGN" fill="#ef4444" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Detailed Table */}
              <motion.div variants={item}>
                <Card>
                  <CardHeader>
                    <CardTitle>Detailed Comparison</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Metric</TableHead>
                          <TableHead className="text-right">M/M/N (Baseline)</TableHead>
                          <TableHead className="text-right">M/G/N (Heavy-Tailed)</TableHead>
                          <TableHead className="text-right">Impact</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow>
                          <TableCell className="font-medium">Mean Wait (Wq)</TableCell>
                          <TableCell className="text-right">{(metrics.mmn.mean_waiting_time * 1000).toFixed(2)} ms</TableCell>
                          <TableCell className="text-right">{(metrics.mgn.mean_waiting_time * 1000).toFixed(2)} ms</TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end items-center gap-2">
                              {(() => {
                                const change = getPercentChange(metrics.mgn.mean_waiting_time, metrics.mmn.mean_waiting_time);
                                return (
                                  <span className={cn(
                                    "flex items-center text-xs font-bold px-2 py-1 rounded-full",
                                    change > 0 ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" : "bg-green-100 text-green-700"
                                  )}>
                                    {change > 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                                    {Math.abs(change).toFixed(1)}%
                                  </span>
                                );
                              })()}
                            </div>
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">Response Time (R)</TableCell>
                          <TableCell className="text-right">{(metrics.mmn.mean_response_time * 1000).toFixed(2)} ms</TableCell>
                          <TableCell className="text-right">{(metrics.mgn.mean_response_time * 1000).toFixed(2)} ms</TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end items-center gap-2">
                              {(() => {
                                const change = getPercentChange(metrics.mgn.mean_response_time, metrics.mmn.mean_response_time);
                                return (
                                  <span className={cn(
                                    "flex items-center text-xs font-bold px-2 py-1 rounded-full",
                                    change > 0 ? "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400" : "bg-green-100 text-green-700"
                                  )}>
                                    {change > 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                                    {Math.abs(change).toFixed(1)}%
                                  </span>
                                );
                              })()}
                            </div>
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">Variability (CV²)</TableCell>
                          <TableCell className="text-right">1.00</TableCell>
                          <TableCell className="text-right">{metrics.mgn.cv_squared.toFixed(2)}</TableCell>
                          <TableCell className="text-right">
                            <span className="text-xs text-muted-foreground">
                              {metrics.mgn.cv_squared > 1 ? "High Variance" : "Low Variance"}
                            </span>
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          ) : (
            <div className="flex h-full items-center justify-center p-8 text-muted-foreground">
              {isUnstable ? "System Unstable" : "Loading..."}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
