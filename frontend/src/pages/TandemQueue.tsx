import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend
} from 'recharts';
import {
  AlertCircle, Activity, Clock, Server, Network, ArrowRight, RefreshCw, Zap, TrendingUp
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

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

export const TandemQueue = () => {
  // State
  const [lambda, setLambda] = useState(20);
  const [n1, setN1] = useState(4);
  const [mu1, setMu1] = useState(10);
  const [n2, setN2] = useState(4);
  const [mu2, setMu2] = useState(10);
  const [networkDelay, setNetworkDelay] = useState(0.05);
  const [failureProb, setFailureProb] = useState(0.1);
  const [isBursty, setIsBursty] = useState(false); // Toggle for "Pareto" input

  const [metrics, setMetrics] = useState<TandemMetrics | null>(null);

  // Real-time Data for Graphs
  const [node1Data, setNode1Data] = useState<any[]>([]);
  const [node2Data, setNode2Data] = useState<any[]>([]);
  const maxDataPoints = 50;

  // Derived
  const rho1 = lambda / (n1 * mu1);
  const lambda2 = lambda / (1 - failureProb);
  const rho2 = lambda2 / (n2 * mu2);
  const isUnstable = rho1 >= 1 || rho2 >= 1;

  // --- Analytical Calculation ---
  useEffect(() => {
    const calculate = async () => {
      try {
        const response = await axios.post('/api/analytical/tandem', {
          arrival_rate: lambda,
          n1: n1, mu1: mu1, n2: n2, mu2: mu2,
          network_delay: networkDelay, failure_prob: failureProb,
          consistency_mode: 'out_of_order'
        });
        setMetrics(response.data.metrics);
      } catch (err) {
        console.error(err);
      }
    };
    const timer = setTimeout(calculate, 100);
    return () => clearTimeout(timer);
  }, [lambda, n1, mu1, n2, mu2, networkDelay, failureProb]);

  // --- Visual Simulation Loop (The Blast Radius Effect) ---
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date().toLocaleTimeString();

      // Simulate Node 1 Latency
      // If Bursty, use Pareto-like spikes. Else Exponential.
      let lat1 = (1 / mu1) * 1000; // Base service time
      if (isBursty) {
        if (Math.random() > 0.9) lat1 *= (5 + Math.random() * 10); // Spikes
      } else {
        lat1 += (Math.random() - 0.5) * 20; // Noise
      }
      // Queueing effect
      lat1 = lat1 / (1 - Math.min(rho1, 0.99));

      // Simulate Node 2 Latency (The Amplification)
      // Node 2 sees the output of Node 1. 
      // If Node 1 is bursty, Node 2 sees "clumped" arrivals -> Higher Variance -> Higher Latency.
      // Burke's Theorem says Output is Poisson ONLY if Service is Exponential.
      // But here we have Pareto (Bursty) input or just high load.
      // We simulate amplification by adding MORE variance to Node 2 if Node 1 is bursty.

      let lat2 = (1 / mu2) * 1000;
      let amplification = 1.0;

      if (isBursty) {
        // Burst propagation!
        // If Node 1 spiked recently, Node 2 gets flooded.
        // We simulate this by correlating Node 2's spike probability with Node 1's.
        if (lat1 > 500) {
          amplification = 2.5; // Massive amplification
        }
        // Also random spikes are more frequent/severe in Node 2 due to "clumping"
        if (Math.random() > 0.85) lat2 *= (8 + Math.random() * 15);
      } else {
        lat2 += (Math.random() - 0.5) * 20;
      }

      lat2 = (lat2 * amplification) / (1 - Math.min(rho2, 0.99));

      // Update Graphs
      setNode1Data(prev => {
        const next = [...prev, { time: now, latency: Math.min(lat1, 3000) }];
        if (next.length > maxDataPoints) next.shift();
        return next;
      });
      setNode2Data(prev => {
        const next = [...prev, { time: now, latency: Math.min(lat2, 3000) }];
        if (next.length > maxDataPoints) next.shift();
        return next;
      });

    }, 200); // 5Hz update

    return () => clearInterval(interval);
  }, [lambda, mu1, mu2, rho1, rho2, isBursty]);


  return (
    <div className="space-y-8 pb-10">
      <div className="flex justify-between items-center">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">The Blast Radius</h1>
          <p className="text-muted-foreground">
            Visualizing Network Effects & Burst Propagation (Tandem Queue).
          </p>
        </div>
        <div className="flex items-center gap-4 bg-muted p-2 rounded-lg">
          <Label className={cn("font-bold", isBursty ? "text-red-500" : "text-green-500")}>
            {isBursty ? "⚠️ Bursty Workload (Pareto)" : "🟢 Smooth Workload (Poisson)"}
          </Label>
          <Switch checked={isBursty} onCheckedChange={setIsBursty} />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Controls */}
        <Card className="lg:col-span-3 h-fit">
          <CardHeader>
            <CardTitle>Pipeline Config</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Input Traffic (λ)</Label>
              <Slider value={[lambda]} onValueChange={(v) => setLambda(v[0])} min={5} max={100} />
              <span className="text-xs text-muted-foreground">{lambda} req/s</span>
            </div>
            <div className="space-y-2">
              <Label>Node 1 Capacity (μ1)</Label>
              <Slider value={[mu1]} onValueChange={(v) => setMu1(v[0])} min={5} max={50} />
              <span className="text-xs text-muted-foreground">{mu1} req/s</span>
            </div>
            <div className="space-y-2">
              <Label>Node 2 Capacity (μ2)</Label>
              <Slider value={[mu2]} onValueChange={(v) => setMu2(v[0])} min={5} max={50} />
              <span className="text-xs text-muted-foreground">{mu2} req/s</span>
            </div>
            <div className="space-y-2">
              <Label>Failure Prob (p)</Label>
              <Slider value={[failureProb]} onValueChange={(v) => setFailureProb(v[0])} min={0} max={0.5} step={0.05} />
              <span className="text-xs text-muted-foreground">{(failureProb * 100).toFixed(0)}%</span>
            </div>
          </CardContent>
        </Card>

        {/* Visuals */}
        <div className="lg:col-span-9 space-y-6">
          {/* The Blast Radius Graphs */}
          <div className="grid md:grid-cols-2 gap-4">
            {/* Node 1 */}
            <Card className={cn("border-l-4", isBursty ? "border-l-orange-500" : "border-l-green-500")}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Node 1: The Source</CardTitle>
                <CardDescription>Processing Input Traffic</CardDescription>
              </CardHeader>
              <CardContent className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={node1Data}>
                    <YAxis domain={[0, 2000]} hide />
                    <Line type="monotone" dataKey="latency" stroke="#f97316" strokeWidth={2} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
                <div className="text-center text-xs font-mono mt-2">Variance: {isBursty ? "HIGH" : "LOW"}</div>
              </CardContent>
            </Card>

            {/* Node 2 */}
            <Card className={cn("border-l-4", isBursty ? "border-l-red-600" : "border-l-green-500")}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Node 2: The Victim</CardTitle>
                <CardDescription>Processing Node 1 Output</CardDescription>
              </CardHeader>
              <CardContent className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={node2Data}>
                    <YAxis domain={[0, 2000]} hide />
                    <Line type="monotone" dataKey="latency" stroke="#dc2626" strokeWidth={2} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
                <div className="text-center text-xs font-mono mt-2 font-bold text-red-500">
                  Variance: {isBursty ? "EXTREME (Amplified)" : "LOW"}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Metrics */}
          {metrics && (
            <Card>
              <CardHeader><CardTitle className="text-sm">System Metrics</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-sm text-muted-foreground">Total Latency</div>
                    <div className="text-2xl font-bold">{(metrics.total_latency * 1000).toFixed(0)} ms</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Load Amplification</div>
                    <div className="text-2xl font-bold text-orange-500">
                      {(metrics.load_amplification * 100 - 100).toFixed(0)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Node 2 Utilization</div>
                    <div className="text-2xl font-bold">
                      {(metrics.stage2_utilization * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
