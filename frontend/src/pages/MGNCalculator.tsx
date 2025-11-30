import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import {
  AlertTriangle,
  Activity,
  Clock,
  Zap,
  BarChart2,
  Info
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { cn } from '@/lib/utils';

// Types
interface MGNMetrics {
  mean_waiting_time: number;
  mean_response_time: number;
  cv_squared: number;
  p99_response_time_heavy_tail: number;
}

export const MGNCalculator = () => {
  // State
  const [lambda, setLambda] = useState(100);
  const [mu, setMu] = useState(12);
  const [N, setN] = useState(10);
  const [alpha, setAlpha] = useState(2.5);
  const [distribution, setDistribution] = useState<'pareto' | 'lognormal' | 'weibull'>('pareto');

  const [metrics, setMetrics] = useState<MGNMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Derived
  const rho = lambda / (N * mu);
  const isUnstable = rho >= 1;
  const cv2 = alpha > 2 ? 1 / (alpha * (alpha - 2)) : 10;
  const meanService = 1 / mu;
  const scale = meanService * (alpha - 1) / alpha;

  // Calculation Effect
  useEffect(() => {
    const calculate = async () => {
      setLoading(true);
      setError(null);
      try {
        const variance = cv2 * meanService * meanService;
        const response = await axios.post('/api/analytical/mgn', {
          arrival_rate: lambda,
          num_threads: N,
          mean_service: meanService,
          variance_service: variance,
        });
        setMetrics(response.data.metrics);
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Calculation failed');
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(calculate, 100);
    return () => clearTimeout(timer);
  }, [lambda, mu, N, alpha, distribution]);

  // Generate Distribution Data for Chart
  const generateChartData = () => {
    const data = [];
    for (let i = 1; i <= 100; i++) {
      const x = i * 0.002; // Time points

      // Exponential (M/M/N baseline)
      const expY = mu * Math.exp(-mu * x);

      // Pareto (Heavy-tailed)
      let paretoY = 0;
      if (x >= scale) {
        paretoY = (alpha * Math.pow(scale, alpha)) / Math.pow(x, alpha + 1);
      }

      data.push({
        time: x,
        exponential: expY > 100 ? null : expY, // Clip extreme values for chart
        pareto: paretoY > 100 ? null : paretoY
      });
    }
    return data;
  };

  const chartData = generateChartData();

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
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">M/G/N Calculator</h1>
        <p className="text-muted-foreground">
          Analyze systems with heavy-tailed service time distributions (Pareto, Lognormal).
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Controls */}
        <Card className="lg:col-span-4 h-fit">
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
            <CardDescription>Heavy-tail parameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Distribution Select */}
            <div className="space-y-2">
              <Label>Distribution Type</Label>
              <Select
                value={distribution}
                onValueChange={(v: any) => setDistribution(v)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select distribution" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pareto">Pareto (Heavy-Tailed)</SelectItem>
                  <SelectItem value="lognormal">Lognormal</SelectItem>
                  <SelectItem value="weibull">Weibull</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Alpha Slider */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <Label className="text-base font-medium">Shape Parameter (α)</Label>
                <span className={cn(
                  "text-sm font-mono px-2 py-1 rounded",
                  alpha <= 2.1 ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" : "bg-muted"
                )}>
                  α = {alpha}
                </span>
              </div>
              <Slider
                value={[alpha]}
                onValueChange={(v: number[]) => setAlpha(v[0])}
                min={2.1}
                max={5.0}
                step={0.1}
                className="py-2"
              />
              <p className="text-xs text-muted-foreground">
                Lower α = Heavier tail (more extreme outliers). α ≤ 2 has infinite variance.
              </p>
            </div>

            {/* Standard Parameters */}
            <div className="space-y-4 pt-4 border-t">
              <Label>System Load</Label>

              <div className="space-y-4">
                <div className="flex justify-between text-sm">
                  <span>Arrival Rate (λ)</span>
                  <span className="font-mono">{lambda}</span>
                </div>
                <Slider value={[lambda]} onValueChange={(v: number[]) => setLambda(v[0])} min={10} max={200} step={5} />

                <div className="flex justify-between text-sm">
                  <span>Service Rate (μ)</span>
                  <span className="font-mono">{mu}</span>
                </div>
                <Slider value={[mu]} onValueChange={(v: number[]) => setMu(v[0])} min={5} max={50} step={1} />

                <div className="flex justify-between text-sm">
                  <span>Threads (N)</span>
                  <span className="font-mono">{N}</span>
                </div>
                <Slider value={[N]} onValueChange={(v: number[]) => setN(v[0])} min={1} max={30} step={1} />
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
              {/* Metrics Grid */}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <motion.div variants={item}>
                  <Card className="bg-secondary/20">
                    <CardHeader className="p-4 pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">Mean Wait</CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0">
                      <div className="text-2xl font-bold">{(metrics.mean_waiting_time * 1000).toFixed(1)} ms</div>
                    </CardContent>
                  </Card>
                </motion.div>
                <motion.div variants={item}>
                  <Card className="bg-secondary/20">
                    <CardHeader className="p-4 pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">Response Time</CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0">
                      <div className="text-2xl font-bold">{(metrics.mean_response_time * 1000).toFixed(1)} ms</div>
                    </CardContent>
                  </Card>
                </motion.div>
                <motion.div variants={item}>
                  <Card className={cn("bg-secondary/20", cv2 > 5 && "border-orange-500/50 bg-orange-500/10")}>
                    <CardHeader className="p-4 pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">Variability (CV²)</CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0">
                      <div className="text-2xl font-bold">{metrics.cv_squared.toFixed(2)}</div>
                    </CardContent>
                  </Card>
                </motion.div>
                <motion.div variants={item}>
                  <Card className="bg-secondary/20">
                    <CardHeader className="p-4 pb-2">
                      <CardTitle className="text-sm font-medium text-muted-foreground">Penalty Factor</CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 pt-0">
                      <div className="text-2xl font-bold">{((1 + metrics.cv_squared) / 2).toFixed(2)}x</div>
                    </CardContent>
                  </Card>
                </motion.div>
              </div>

              {/* Distribution Chart */}
              <motion.div variants={item}>
                <Card>
                  <CardHeader>
                    <CardTitle>Service Time Distribution Comparison</CardTitle>
                    <CardDescription>
                      Exponential (M/M/N) vs. {distribution === 'pareto' ? 'Pareto' : 'Heavy-Tailed'} (M/G/N)
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="h-[400px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                        <XAxis
                          dataKey="time"
                          label={{ value: 'Service Time (s)', position: 'insideBottomRight', offset: -10 }}
                          tickFormatter={(v) => v.toFixed(2)}
                        />
                        <YAxis
                          label={{ value: 'Probability Density', angle: -90, position: 'insideLeft' }}
                        />
                        <RechartsTooltip
                          formatter={(value: number) => value.toFixed(4)}
                          labelFormatter={(label) => `Time: ${Number(label).toFixed(3)}s`}
                        />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="exponential"
                          name="Exponential (Baseline)"
                          stroke="#3b82f6"
                          strokeWidth={2}
                          dot={false}
                        />
                        <Line
                          type="monotone"
                          dataKey="pareto"
                          name={`Pareto (α=${alpha})`}
                          stroke="#ef4444"
                          strokeWidth={2}
                          strokeDasharray="5 5"
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Explanation */}
              <motion.div variants={item}>
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertTitle>Understanding Heavy Tails</AlertTitle>
                  <AlertDescription className="mt-2 text-sm text-muted-foreground">
                    In a heavy-tailed distribution (like Pareto with low α), most requests are small, but a few are
                    <strong> extremely large</strong>. These "stragglers" block threads and cause queueing delays
                    disproportionate to the average load. Kingman's approximation (used here) quantifies this
                    via the Variability Factor: <code>(1 + CV²) / 2</code>.
                  </AlertDescription>
                </Alert>
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
