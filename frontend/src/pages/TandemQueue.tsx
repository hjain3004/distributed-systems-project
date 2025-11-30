import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { TandemEquation1, TandemEquation2, TandemEquation3 } from '../components/MathEquation';

export const TandemQueue = () => {
  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Tandem Queue Model</h1>
        <p className="text-muted-foreground">
          Two-Stage Broker→Receiver Architecture (Li et al. 2015)
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Critical Equations</CardTitle>
          <CardDescription>
            Mathematical foundation for the two-stage system with reliability guarantees.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-6">
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <TandemEquation1 />
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <TandemEquation2 />
            </div>
            <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-4">
              <TandemEquation3 />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
