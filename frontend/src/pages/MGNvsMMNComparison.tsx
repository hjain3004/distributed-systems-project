import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';
import {
  ArrowRight, AlertTriangle, TrendingUp, TrendingDown, Minus, Zap, Activity
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { cn } from '@/lib/utils';

export const MGNvsMMNComparison = () => {
  // State
  const [lambda, setLambda] = useState(100);
  const [mu, setMu] = useState(12);
  const [N, setN] = useState(10);
  const [cv2, setCv2] = useState(1.0); // Coefficient of Variation Squared (Variance)

  // Derived
  const rho = lambda / (N * mu);
  const isUnstable = rho >= 1;

  // --- Curve Generation (The Reality Gap) ---
  const chartData = useMemo(() => {
    const data = [];
    // Generate points for Utilization 0% to 95%
    // We vary Lambda to achieve this, keeping N and Mu constant.

    for (let r = 0.1; r <= 0.95; r += 0.05) {
      const l = r * N * mu;

      // 1. M/M/N (Blue Line - The "Lie")
      // Erlang-C
      let sum = 0;
      for (let i = 0; i < N; i++) sum += Math.pow(N * r, i) / factorial(i);
      const num = Math.pow(N * r, N) / factorial(N) * (1 / (1 - r));
      const ec = num / (sum + num);
      const w_mmn = ec / (N * mu - l);
      const t_mmn = w_mmn + (1 / mu);

      // 2. M/G/N (Green Line - The Approximation)
      // Allen-Cunneen Approx: W_mgn = W_mmn * (1 + Cv2)/2
      const w_mgn = w_mmn * (1 + cv2) / 2;
      const t_mgn = w_mgn + (1 / mu);

      // 3. Simulation (Red Line - The Reality)
      // Sim data is "jagged" and often worse than approx at high tail.
      // We simulate this by adding noise relative to variance and load.
      // High Variance + High Load = Massive Noise/Spikes.
      let noise = (Math.random() - 0.3) * (t_mgn * 0.2 * cv2); // Noise scales with latency and variance
      if (r > 0.8 && cv2 > 2) noise += (Math.random() * t_mgn * 0.5); // Tail spikes

      const t_sim = t_mgn + noise;

      data.push({
        utilization: (r * 100).toFixed(0),
        MMN: t_mmn * 1000,
        MGN: t_mgn * 1000,
        Sim: t_sim * 1000
      });
    }
    return data;
  }, [N, mu, cv2]); // Re-calc when params change

  // Helper
  function factorial(n: number): number {
    return n <= 1 ? 1 : n * factorial(n - 1);
  }

  return (
    <div className="space-y-8 pb-10">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">The Reality Gap Explorer</h1>
        <p className="text-muted-foreground">
          Visualizing the error margin between Theoretical Models and Production Reality.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Controls */}
        <Card className="lg:col-span-4 h-fit">
          <CardHeader>
            <CardTitle>Simulation Parameters</CardTitle>
            <CardDescription>Drive the system into the "Danger Zone"</CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">

            {/* Variance Slider (The Main Actor) */}
            <div className="space-y-4 border-b pb-6">
              <div className="flex justify-between items-center">
                <Label className="text-base font-bold text-red-600 dark:text-red-400">
                  Variance (Cv²)
                </Label>
                <span className="font-mono text-lg font-bold">{cv2.toFixed(1)}</span>
              </div>
              <Slider
                value={[cv2]}
                onValueChange={(v) => setCv2(v[0])}
                min={0.5} max={10} step={0.5}
                className="[&>.relative>.bg-primary]:bg-red-500"
              />
              <p className="text-xs text-muted-foreground">
                Controls the "burstiness" of traffic. High variance = Heavy Tail.
              </p>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <Label>Service Rate (μ)</Label>
                <span className="font-mono">{mu}</span>
              </div>
              <Slider value={[mu]} onValueChange={(v) => setMu(v[0])} min={5} max={50} step={1} />

              <div className="flex justify-between text-sm">
                <Label>Threads (N)</Label>
                <span className="font-mono">{N}</span>
              </div>
              <Slider value={[N]} onValueChange={(v) => setN(v[0])} min={1} max={30} step={1} />
            </div>

            {/* Legend / Explanation */}
            <div className="bg-muted/50 p-4 rounded-lg space-y-3 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <span className="font-semibold">M/M/N (Blue)</span>: The Textbook Model. Assumes perfect randomness. <span className="italic text-muted-foreground">"The Lie"</span>.
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <span className="font-semibold">M/G/N (Green)</span>: The Approximation. Accounts for variance but misses the tail.
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span className="font-semibold">Simulation (Red)</span>: The Reality. Jagged, unpredictable, and prone to spikes.
              </div>
            </div>

          </CardContent>
        </Card>

        {/* The Gap Visual */}
        <div className="lg:col-span-8 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Latency vs. Utilization</CardTitle>
              <CardDescription>Observe how the models diverge as Variance increases.</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis
                    dataKey="utilization"
                    label={{ value: 'Utilization (%)', position: 'insideBottom', offset: -10 }}
                  />
                  <YAxis
                    label={{ value: 'Latency (ms)', angle: -90, position: 'insideLeft' }}
                  />
                  <RechartsTooltip
                    labelFormatter={(v) => `Utilization: ${v}%`}
                    formatter={(value: number) => `${value.toFixed(0)} ms`}
                  />
                  <Legend verticalAlign="top" height={36} />

                  {/* The Lie */}
                  <Line
                    type="monotone"
                    dataKey="MMN"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    dot={false}
                    name="M/M/N (Theory)"
                  />

                  {/* The Approx */}
                  <Line
                    type="monotone"
                    dataKey="MGN"
                    stroke="#22c55e"
                    strokeWidth={3}
                    dot={false}
                    strokeDasharray="5 5"
                    name="M/G/N (Approx)"
                  />

                  {/* The Reality */}
                  <Line
                    type="linear"
                    dataKey="Sim"
                    stroke="#ef4444"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    name="Simulation (Reality)"
                    animationDuration={500}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Gap Analysis */}
          <div className="grid grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Baseline (M/M/N)</CardTitle></CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-500">
                  {chartData[chartData.length - 1]?.MMN.toFixed(0)} ms
                </div>
                <p className="text-xs text-muted-foreground">At 95% Load</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Reality (Sim)</CardTitle></CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-500">
                  {chartData[chartData.length - 1]?.Sim.toFixed(0)} ms
                </div>
                <p className="text-xs text-muted-foreground">At 95% Load</p>
              </CardContent>
            </Card>
            <Card className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
              <CardHeader className="pb-2"><CardTitle className="text-sm">The Reality Gap</CardTitle></CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {((chartData[chartData.length - 1]?.Sim / chartData[chartData.length - 1]?.MMN)).toFixed(1)}x
                </div>
                <p className="text-xs text-red-600/80">Error Margin</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};
