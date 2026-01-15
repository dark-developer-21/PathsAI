import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import VoiceAssistant from './pages/VoiceAssistant';
import MapNavigation from './pages/MapNavigation';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="voice" element={<VoiceAssistant />} />
          <Route path="map" element={<MapNavigation />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
