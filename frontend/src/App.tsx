import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import { Dashboard } from './pages/Dashboard';
import { MGNvsMMNComparison } from './pages/MGNvsMMNComparison';
import { AllEquations } from './pages/AllEquations';
import { MMNCalculator } from './pages/MMNCalculator';
import { MGNCalculator } from './pages/MGNCalculator';
import { ControlCenter } from './pages/ControlCenter';
import { TandemQueue } from './pages/TandemQueue';
import { ResultsViewer } from './pages/ResultsViewer';
import { SimulationProvider } from './context/SimulationContext';

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <SimulationProvider>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/control" element={<ControlCenter />} />
            <Route path="/compare" element={<MGNvsMMNComparison />} />
            <Route path="/mmn" element={<MMNCalculator />} />
            <Route path="/mgn" element={<MGNCalculator />} />
            <Route path="/tandem" element={<TandemQueue />} />
            <Route path="/results" element={<ResultsViewer />} />
            <Route path="/equations" element={<AllEquations />} />
          </Routes>
        </AppLayout>
      </SimulationProvider>
    </BrowserRouter>
  );
}

export default App;
