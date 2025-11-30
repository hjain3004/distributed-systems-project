import React from 'react';
import {
  Equation1,
  Equation2,
  Equation3,
  Equation4,
  Equation5,
  Equation6,
  Equation7,
  Equation8,
  Equation9,
  Equation10,
  Equation11,
  Equation12,
  Equation13,
  Equation14,
  Equation15,
  TandemEquation1,
  TandemEquation2,
  TandemEquation3,
  TandemEquation4,
  TandemEquation5,
} from '../components/MathEquation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

export const AllEquations = () => {
  return (
    <div className="space-y-8 pb-10">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Analytical Framework</h1>
        <p className="text-muted-foreground">
          Comprehensive reference of all 15 core queueing theory equations used in the system.
        </p>
      </div>

      {/* Section 1: M/M/N Baseline */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl text-primary">Section 1: M/M/N Baseline</CardTitle>
            <Badge variant="default">Equations 1-5</Badge>
          </div>
          <CardDescription>
            Standard Markovian model with exponential service times (C² = 1).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <Equation1 />
              <p className="mt-2 text-xs text-muted-foreground">
                System utilization (ρ). Must be &lt; 1 for stability.
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <Equation2 />
              <p className="mt-2 text-xs text-muted-foreground">
                Erlang-C formula: Probability that an arriving customer must wait.
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <Equation3 />
              <p className="mt-2 text-xs text-muted-foreground">
                Probability system is empty (P₀).
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <Equation4 />
              <p className="mt-2 text-xs text-muted-foreground">
                Mean queue length (Lq).
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4 md:col-span-2">
              <Equation5 />
              <p className="mt-2 text-xs text-muted-foreground">
                Mean waiting time (Wq) - Little's Law application.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section 2: M/G/N Heavy-Tailed */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl text-destructive">Section 2: M/G/N Heavy-Tailed</CardTitle>
            <Badge variant="destructive">Equations 6-10</Badge>
          </div>
          <CardDescription>
            General service time distribution (Pareto) modeling real-world variance.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4 md:col-span-2 lg:col-span-3">
              <Equation6 />
              <p className="mt-2 text-xs text-muted-foreground">
                Pareto PDF. Shape parameter α controls tail heaviness.
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <Equation7 />
              <p className="mt-2 text-xs text-muted-foreground">
                Mean service time (E[S]).
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <Equation8 />
              <p className="mt-2 text-xs text-muted-foreground">
                Second moment (E[S²]).
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <Equation9 />
              <p className="mt-2 text-xs text-muted-foreground">
                Squared Coefficient of Variation (C²).
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4 md:col-span-2 lg:col-span-3">
              <Equation10 />
              <p className="mt-2 text-xs text-muted-foreground">
                Pollaczek-Khinchin approximation for M/G/N mean waiting time.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section 3: Threading Models */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl text-green-600 dark:text-green-400">Section 3: Threading Models</CardTitle>
            <Badge className="bg-green-600 hover:bg-green-700">Equations 11-15</Badge>
          </div>
          <CardDescription>
            Concurrency limits and overhead analysis.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <Equation11 />
              <p className="mt-2 text-xs text-muted-foreground">
                Max concurrent connections (N_max).
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <Equation12 />
              <p className="mt-2 text-xs text-muted-foreground">
                System throughput (X).
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <Equation13 />
              <p className="mt-2 text-xs text-muted-foreground">
                Effective service rate with contention (μ').
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <Equation14 />
              <p className="mt-2 text-xs text-muted-foreground">
                Saturation probability (P_sat).
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4 md:col-span-2">
              <Equation15 />
              <p className="mt-2 text-xs text-muted-foreground">
                99th percentile response time (Normal approx - inaccurate for heavy tails).
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Bonus: Tandem Queue */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl text-blue-600 dark:text-blue-400">Bonus: Tandem Queue</CardTitle>
            <Badge className="bg-blue-600 hover:bg-blue-700">Li et al. 2015</Badge>
          </div>
          <CardDescription>
            Multi-stage architecture with reliability guarantees (retries).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <TandemEquation1 />
              <p className="mt-2 text-xs text-muted-foreground">
                Stage 1 utilization (ρ₁).
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <TandemEquation2 />
              <p className="mt-2 text-xs text-muted-foreground">
                Stage 2 effective arrival rate (Λ₂). Includes retries!
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <TandemEquation3 />
              <p className="mt-2 text-xs text-muted-foreground">
                Stage 2 utilization (ρ₂).
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <TandemEquation4 />
              <p className="mt-2 text-xs text-muted-foreground">
                Expected network time (E[T_net]).
              </p>
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4 md:col-span-2">
              <TandemEquation5 />
              <p className="mt-2 text-xs text-muted-foreground">
                Total end-to-end latency (E[T]).
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
