import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

export const ResultsViewer = () => {
  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Results Viewer</h1>
        <p className="text-muted-foreground">
          Browse and analyze simulation results.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Simulation History</CardTitle>
          <CardDescription>
            View past simulation runs and their outcomes.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-48 text-muted-foreground border-2 border-dashed rounded-lg">
            No results available yet. Run a simulation to see data here.
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
