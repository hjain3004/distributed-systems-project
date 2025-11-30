import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import { Dashboard } from './pages/Dashboard';
import { MGNvsMMNComparison } from './pages/MGNvsMMNComparison';
import { AllEquations } from './pages/AllEquations';
import { MMNCalculator } from './pages/MMNCalculator';
import { MGNCalculator } from './pages/MGNCalculator';
import { TandemQueue } from './pages/TandemQueue';
import { ResultsViewer } from './pages/ResultsViewer';

function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/compare" element={<MGNvsMMNComparison />} />
          <Route path="/mmn" element={<MMNCalculator />} />
          <Route path="/mgn" element={<MGNCalculator />} />
          <Route path="/tandem" element={<TandemQueue />} />
          <Route path="/equations" element={<AllEquations />} />
          <Route path="/results" element={<ResultsViewer />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}

export default App;
