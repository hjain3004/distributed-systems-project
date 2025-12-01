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
  AlertCircle,
  Activity,
  Clock,
  Server,
  Network,
  ArrowRight,
  RefreshCw
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { cn } from '@/lib/utils';

// Types
interface TandemMetrics {
  stage1_waiting_time: number;
  stage1_utilization: number;
  stage2_waiting_time: number;
  stage2_effective_arrival: number;
  stage2_utilization: number;
  network_time: number;
  total_latency: number;
  load_amplification: number;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b']; // Blue, Green, Amber

export const TandemQueue = () => {
  // State
  const [lambda, setLambda] = useState(20);
  const [n1, setN1] = useState(4);
  const [mu1, setMu1] = useState(10);
  const [n2, setN2] = useState(4);
  const [mu2, setMu2] = useState(10);
  const [networkDelay, setNetworkDelay] = useState(0.05); // 50ms
  const [failureProb, setFailureProb] = useState(0.1); // 10%
  const [consistencyMode, setConsistencyMode] = useState<'in_order' | 'out_of_order'>('out_of_order');

  const [metrics, setMetrics] = useState<TandemMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Derived
  const rho1 = lambda / (n1 * mu1);
  const lambda2 = lambda / (1 - failureProb);
  const rho2 = lambda2 / (n2 * mu2);
  const isUnstable = rho1 >= 1 || rho2 >= 1;

  // Calculation Effect
  useEffect(() => {
    const calculate = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.post('/api/analytical/tandem', {
          arrival_rate: lambda,
          n1: n1,
          mu1: mu1,
          n2: n2,
          mu2: mu2,
          network_delay: networkDelay,
          failure_prob: failureProb,
          consistency_mode: consistencyMode
        });
        setMetrics(response.data.metrics);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Calculation failed');
      } finally {
        setLoading(false);
      }
    };

    // Debounce
    const timer = setTimeout(calculate, 100);
    return () => clearTimeout(timer);
  }, [lambda, n1, mu1, n2, mu2, networkDelay, failureProb, consistencyMode]);

  // Animation variants
  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  const chartData = metrics ? [
    { name: 'Stage 1 (Broker)', value: metrics.stage1_waiting_time + (1 / mu1), fill: COLORS[0] },
    { name: 'Network (Retries)', value: metrics.network_time, fill: COLORS[1] },
    { name: 'Stage 2 (Receiver)', value: metrics.stage2_waiting_time + (1 / mu2), fill: COLORS[2] },
  ] : [];

  return (
    <div className="space-y-8 pb-10">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Tandem Queue Model</h1>
        <p className="text-muted-foreground">
          Two-stage architecture with reliability guarantees (Li et al. 2015).
          Visualizing the impact of retransmissions on system load.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Controls Panel */}
        <Card className="lg:col-span-4 h-fit">
          <CardHeader>
            <CardTitle>System Parameters</CardTitle>
            <CardDescription>Configure the two-stage pipeline</CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">

            {/* Global Arrival */}
            <div className="space-y-4 border-b pb-4">
              <div className="flex justify-between items-center">
                <Label className="text-base font-medium text-primary">Global Arrival (λ)</Label>
                <span className="text-sm font-mono bg-muted px-2 py-1 rounded">
                  {lambda} msg/s
                </span>
              </div>
              <Slider
                value={[lambda]}
                onValueChange={(v) => setLambda(v[0])}
                min={5}
                max={100}
                step={1}
              />
            </div>

            {/* Stage 1 Config */}
            <div className="space-y-4">
              <Label className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Stage 1: Broker</Label>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Servers (N1)</span>
                  <span className="font-mono">{n1}</span>
                </div>
                <Slider value={[n1]} onValueChange={(v) => setN1(v[0])} min={1} max={20} step={1} />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Service Rate (μ1)</span>
                  <span className="font-mono">{mu1}</span>
                </div>
                <Slider value={[mu1]} onValueChange={(v) => setMu1(v[0])} min={5} max={50} step={1} />
              </div>
            </div>

            {/* Network Config */}
            <div className="space-y-4 border-t pt-4">
              <Label className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Network & Reliability</Label>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Failure Probability (p)</span>
                  <span className="font-mono">{(failureProb * 100).toFixed(0)}%</span>
                </div>
                <Slider
                  value={[failureProb]}
                  onValueChange={(v) => setFailureProb(v[0])}
                  min={0}
                  max={0.5}
                  step={0.01}
                  className="[&>.relative>.bg-primary]:bg-orange-500"
                />
                <p className="text-xs text-muted-foreground">
                  Higher failure = More retries = Traffic Inflation
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Network Delay (D)</span>
                  <span className="font-mono">{(networkDelay * 1000).toFixed(0)} ms</span>
                </div>
                <Slider value={[networkDelay]} onValueChange={(v) => setNetworkDelay(v[0])} min={0.01} max={0.2} step={0.01} />
              </div>
            </div>

            {/* Stage 2 Config */}
            <div className="space-y-4 border-t pt-4">
              <Label className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Stage 2: Receiver</Label>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Servers (N2)</span>
                  <span className="font-mono">{n2}</span>
                </div>
                <Slider value={[n2]} onValueChange={(v) => setN2(v[0])} min={1} max={20} step={1} />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Service Rate (μ2)</span>
                  <span className="font-mono">{mu2}</span>
                </div>
                <Slider value={[mu2]} onValueChange={(v) => setMu2(v[0])} min={5} max={50} step={1} />
              </div>
            </div>

            {/* Consistency Mode */}
            <div className="space-y-4 border-t pt-4">
              <Label className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Consistency Model</Label>
              <div className="flex items-center justify-between space-x-2">
                <Label htmlFor="consistency-mode" className="flex flex-col space-y-1">
                  <span>In-Order Delivery</span>
                  <span className="font-normal text-xs text-muted-foreground">Strict FIFO (Higher Latency)</span>
                </Label>
                <Switch
                  id="consistency-mode"
                  checked={consistencyMode === 'in_order'}
                  onCheckedChange={(checked) => setConsistencyMode(checked ? 'in_order' : 'out_of_order')}
                />
              </div>
            </div>

            {/* Stability Alert */}
            {isUnstable && (
              <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
                <div className="flex items-center gap-2 font-semibold">
                  <AlertCircle className="h-4 w-4" />
                  System Unstable
                </div>
                <p className="mt-1 text-sm">
                  {rho1 >= 1 ? "Stage 1" : "Stage 2"} is overloaded (ρ ≥ 1).
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
              {/* Traffic Inflation Highlight */}
              <motion.div variants={item}>
                <Card className="bg-gradient-to-br from-background to-muted/50 border-primary/20">
                  <CardHeader className="pb-2">
                    <CardTitle className="flex items-center gap-2">
                      <RefreshCw className="h-5 w-5 text-orange-500" />
                      Traffic Inflation Effect
                    </CardTitle>
                    <CardDescription>
                      Impact of retransmissions on Stage 2 load
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-around py-4">
                      <div className="text-center">
                        <div className="text-sm text-muted-foreground">Original Traffic (λ)</div>
                        <div className="text-3xl font-bold">{lambda}</div>
                        <div className="text-xs text-muted-foreground">msg/sec</div>
                      </div>

                      <ArrowRight className="h-8 w-8 text-muted-foreground/50" />

                      <div className="text-center">
                        <div className="text-sm text-muted-foreground">Failure Rate (p)</div>
                        <div className="text-3xl font-bold text-orange-500">{(failureProb * 100).toFixed(0)}%</div>
                        <div className="text-xs text-muted-foreground">Retries</div>
                      </div>

                      <ArrowRight className="h-8 w-8 text-muted-foreground/50" />

                      <div className="text-center">
                        <div className="text-sm text-muted-foreground">Effective Traffic (Λ₂)</div>
                        <div className="text-3xl font-bold text-red-500">{metrics.stage2_effective_arrival.toFixed(1)}</div>
                        <div className="text-xs text-muted-foreground">msg/sec</div>
                      </div>
                    </div>
                    <div className="mt-4 text-center text-sm font-medium text-muted-foreground bg-background/50 py-2 rounded-md border">
                      Load Amplification: <span className="text-foreground">{(metrics.load_amplification * 100 - 100).toFixed(1)}% extra traffic</span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Latency Chart */}
              <motion.div variants={item}>
                <Card>
                  <CardHeader>
                    <CardTitle>End-to-End Latency Breakdown</CardTitle>
                    <CardDescription>Where is time being spent?</CardDescription>
                  </CardHeader>
                  <CardContent className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                        <XAxis type="number" unit="s" />
                        <YAxis dataKey="name" type="category" width={120} />
                        <RechartsTooltip
                          formatter={(value: number) => [`${value.toFixed(3)} s`, 'Time']}
                          contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))' }}
                        />
                        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                          {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Detailed Metrics Grid */}
              <div className="grid gap-4 md:grid-cols-3">
                <motion.div variants={item}>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium">Stage 1 Utilization</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className={cn("text-2xl font-bold", metrics.stage1_utilization > 0.8 ? "text-orange-500" : "text-green-500")}>
                        {(metrics.stage1_utilization * 100).toFixed(1)}%
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>

                <motion.div variants={item}>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium">Total Latency</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {(metrics.total_latency * 1000).toFixed(0)} ms
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>

                <motion.div variants={item}>
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium">Stage 2 Utilization</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className={cn("text-2xl font-bold", metrics.stage2_utilization > 0.8 ? "text-orange-500" : "text-green-500")}>
                        {(metrics.stage2_utilization * 100).toFixed(1)}%
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              </div>

            </motion.div>
          ) : (
            <div className="flex h-full items-center justify-center p-8 text-muted-foreground">
              {isUnstable ? "System Overloaded. Increase servers or reduce traffic." : "Loading..."}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
