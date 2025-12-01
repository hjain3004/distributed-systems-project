import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  Calculator,
  Activity,
  GitCompare,
  ArrowRight,
  Server,
  Zap,
  Clock
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

export const Dashboard = () => {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <section className="space-y-4 pt-4">
        <motion.h1
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-4xl font-bold tracking-tight lg:text-5xl bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent"
        >
          Distributed Systems Modeling
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="text-xl text-muted-foreground max-w-2xl"
        >
          Advanced performance analysis and simulation for message queueing systems.
          Compare theoretical models with real-world simulations.
        </motion.p>
      </section>

      {/* Quick Actions */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
      >
        <motion.div variants={item}>
          <Card className="h-full hover:shadow-lg transition-shadow border-primary/20">
            <CardHeader>
              <div className="w-12 h-12 rounded-lg bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center mb-4">
                <Calculator className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <CardTitle>M/M/N Calculator</CardTitle>
              <CardDescription>
                Standard Markovian queueing model analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Calculate response times, queue lengths, and utilization for systems with exponential inter-arrival and service times.
              </p>
              <Link to="/mmn">
                <Button className="w-full group">
                  Open Calculator
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={item}>
          <Card className="h-full hover:shadow-lg transition-shadow border-primary/20">
            <CardHeader>
              <div className="w-12 h-12 rounded-lg bg-green-100 dark:bg-green-900/20 flex items-center justify-center mb-4">
                <Activity className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <CardTitle>M/G/N Calculator</CardTitle>
              <CardDescription>
                General distribution queueing model
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Analyze systems with general service time distributions (e.g., Heavy-tailed, Pareto) using Kingman's approximation.
              </p>
              <Link to="/mgn">
                <Button className="w-full group" variant="secondary">
                  Open Calculator
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={item}>
          <Card className="h-full hover:shadow-lg transition-shadow border-primary/20">
            <CardHeader>
              <div className="w-12 h-12 rounded-lg bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center mb-4">
                <GitCompare className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <CardTitle>Model Comparison</CardTitle>
              <CardDescription>
                Theory vs. Simulation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Compare analytical predictions against discrete-event simulation results to validate model accuracy.
              </p>
              <Link to="/compare">
                <Button className="w-full group" variant="outline">
                  View Comparison
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={item}>
          <Card className="h-full hover:shadow-lg transition-shadow border-primary/20">
            <CardHeader>
              <div className="w-12 h-12 rounded-lg bg-orange-100 dark:bg-orange-900/20 flex items-center justify-center mb-4">
                <Activity className="h-6 w-6 text-orange-600 dark:text-orange-400" />
              </div>
              <CardTitle>Tandem Queue Model</CardTitle>
              <CardDescription>
                Two-stage reliability analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Analyze the impact of network failures and retransmissions on system load (Traffic Inflation).
              </p>
              <Link to="/tandem">
                <Button className="w-full group" variant="secondary">
                  Open Model
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* Key Features / Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="grid gap-4 md:grid-cols-3"
      >
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Simulation Engine
            </CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">SimPy</div>
            <p className="text-xs text-muted-foreground">
              Discrete-event simulation
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Approximation
            </CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Kingman's</div>
            <p className="text-xs text-muted-foreground">
              Heavy-traffic approximation
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Response Time
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">P99 Analysis</div>
            <p className="text-xs text-muted-foreground">
              Tail latency estimation
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
