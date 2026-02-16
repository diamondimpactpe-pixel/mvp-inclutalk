import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/common/Button';

export const OperatorDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const startAttention = () => {
    navigate('/attention');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-display font-bold text-primary-700">IncluTalk</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-700">¡Hola, {user?.full_name}!</span>
            <Button variant="secondary" size="sm" onClick={logout}>Cerrar Sesión</Button>
          </div>
        </div>
      </nav>
      
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          <h2 className="text-3xl font-display font-bold mb-4">Panel del Operador</h2>
          <p className="text-gray-600 mb-8">Inicia una nueva atención inclusiva</p>
          
          <Button onClick={startAttention} size="lg">
            🚀 Iniciar Atención
          </Button>
        </div>
      </div>
    </div>
  );
};
