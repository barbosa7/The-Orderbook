import { Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { TradingPage } from './pages/TradingPage';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route 
          path="/trading" 
          element={
            <ProtectedRoute>
              <TradingPage />
            </ProtectedRoute>
          } 
        />
        <Route path="/" element={<Navigate to="/trading" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App; 