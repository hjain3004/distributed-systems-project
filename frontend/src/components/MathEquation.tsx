/**
 * MathEquation Component
 * Renders LaTeX equations using KaTeX
 */

import { Box } from '@mui/material';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';

interface MathEquationProps {
  equation: string;
  block?: boolean;
  fontSize?: string;
}

export const MathEquation = ({ equation, block = true, fontSize = '1.1rem' }: MathEquationProps) => {
  return (
    <Box sx={{ my: 1, fontSize }}>
      {block ? <BlockMath math={equation} /> : <InlineMath math={equation} />}
    </Box>
  );
};

/**
 * Pre-defined equation components for the 15 core equations
 */

export const Equation1 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 1: Utilization} \quad \rho = \frac{\lambda}{N \cdot \mu}" />
  </Box>
);

export const Equation2 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 2: Erlang-C} \quad C(N,a) = \frac{\frac{a^N}{N!} \cdot \frac{N}{N-a}}{P_0^{-1}}" />
  </Box>
);

export const Equation3 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 3: } P_0 = \left[\sum_{k=0}^{N-1} \frac{a^k}{k!} + \frac{a^N}{N!} \cdot \frac{N}{N-a}\right]^{-1}" />
  </Box>
);

export const Equation4 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 4: Mean Queue Length} \quad L_q = C(N,a) \cdot \frac{\rho}{1-\rho}" />
  </Box>
);

export const Equation5 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 5: Mean Waiting Time} \quad W_q = \frac{L_q}{\lambda} \quad \text{(Little's Law)}" />
  </Box>
);

export const Equation6 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 6: Pareto PDF} \quad f(t) = \frac{\alpha k^\alpha}{t^{\alpha+1}}, \quad t \geq k" />
  </Box>
);

export const Equation7 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 7: Mean Service Time} \quad E[S] = \frac{\alpha k}{\alpha - 1}" />
  </Box>
);

export const Equation8 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 8: Second Moment} \quad E[S^2] = \frac{\alpha k^2}{\alpha - 2}" />
  </Box>
);

export const Equation9 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 9: Coefficient of Variation} \quad C^2 = \frac{1}{\alpha(\alpha-2)}" />
  </Box>
);

export const Equation10 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 10: M/G/N Waiting Time} \quad W_q \approx W_q^{M/M/N} \cdot \frac{1 + C^2}{2}" />
  </Box>
);

export const Equation11 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 11: Max Connections} \quad N_{max} = \frac{N_{threads}}{2}" />
  </Box>
);

export const Equation12 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 12: Throughput} \quad X = \min\left(\lambda, \frac{N_{threads}}{2} \cdot \mu\right)" />
  </Box>
);

export const Equation13 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 13: Effective Service Rate} \quad \mu_{eff} = \frac{\mu}{1 + \alpha \cdot \frac{N_{active}}{N_{threads}}}" />
  </Box>
);

export const Equation14 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 14: Thread Saturation} \quad P_{saturate} = C(N,a) \cdot \rho" />
  </Box>
);

export const Equation15 = () => (
  <Box>
    <MathEquation equation="\text{Eq. 15: P99 Latency} \quad R_{99} \approx E[R] + 2.33 \cdot \sigma_R" />
  </Box>
);

/**
 * Tandem Queue Equations
 */

export const TandemEquation1 = () => (
  <Box>
    <MathEquation equation="\text{Stage 1 Utilization:} \quad \rho_1 = \frac{\lambda}{n_1 \cdot \mu_1}" />
  </Box>
);

export const TandemEquation2 = () => (
  <Box>
    <MathEquation equation="\text{Stage 2 Arrival Rate:} \quad \Lambda_2 = \frac{\lambda}{1-p}" />
  </Box>
);

export const TandemEquation3 = () => (
  <Box>
    <MathEquation equation="\text{Stage 2 Utilization:} \quad \rho_2 = \frac{\Lambda_2}{n_2 \cdot \mu_2} = \frac{\lambda}{(1-p) \cdot n_2 \cdot \mu_2}" />
  </Box>
);

export const TandemEquation4 = () => (
  <Box>
    <MathEquation equation="\text{Network Time:} \quad E[T_{network}] = (2+p) \cdot D_{link}" />
  </Box>
);

export const TandemEquation5 = () => (
  <Box>
    <MathEquation equation="\text{Total Latency:} \quad E[T] = W_1 + S_1 + (2+p) \cdot D + W_2 + S_2" />
  </Box>
);
