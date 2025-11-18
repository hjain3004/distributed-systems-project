/**
 * Main Application Component
 * Routing and layout configuration
 */

import { ThemeProvider, CssBaseline } from '@mui/material';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { theme } from './utils/theme';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { MGNvsMMNComparison } from './pages/MGNvsMMNComparison';
import { AllEquations } from './pages/AllEquations';
import { MMNCalculator } from './pages/MMNCalculator';
import { MGNCalculator } from './pages/MGNCalculator';
import { TandemQueue } from './pages/TandemQueue';
import { ResultsViewer } from './pages/ResultsViewer';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/comparison" element={<MGNvsMMNComparison />} />
            <Route path="/mmn" element={<MMNCalculator />} />
            <Route path="/mgn" element={<MGNCalculator />} />
            <Route path="/tandem" element={<TandemQueue />} />
            <Route path="/equations" element={<AllEquations />} />
            <Route path="/results" element={<ResultsViewer />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
