import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertCircle, RefreshCw } from 'lucide-react';

const ApiHealthCheck = () => {
  const [healthStatus, setHealthStatus] = useState({
    status: 'checking',
    timestamp: null,
    database: null,
    universities_count: null,
    error: null
  });

  const BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const checkApiHealth = async () => {
    setHealthStatus(prev => ({ ...prev, status: 'checking' }));
    
    try {
      const response = await fetch(`${BASE_URL}/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setHealthStatus({
        status: 'healthy',
        timestamp: data.timestamp,
        database: data.database,
        universities_count: data.universities_count,
        error: null
      });
    } catch (error) {
      setHealthStatus({
        status: 'error',
        timestamp: new Date().toISOString(),
        database: 'disconnected',
        universities_count: null,
        error: error.message
      });
    }
  };

  useEffect(() => {
    checkApiHealth();
    const interval = setInterval(checkApiHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = () => {
    switch (healthStatus.status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'checking':
        return <RefreshCw className="h-5 w-5 text-blue-600 animate-spin" />;
      default:
        return <AlertCircle className="h-5 w-5 text-yellow-600" />;
    }
  };

  const getStatusColor = () => {
    switch (healthStatus.status) {
      case 'healthy':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'checking':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      default:
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
    }
  };

  return (
    <div className={`border rounded-lg p-4 ${getStatusColor()}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <span className="font-semibold">
            API Status: {healthStatus.status === 'checking' ? 'Checking...' : healthStatus.status.toUpperCase()}
          </span>
        </div>
        <button
          onClick={checkApiHealth}
          disabled={healthStatus.status === 'checking'}
          className="text-sm underline hover:no-underline disabled:opacity-50"
        >
          Refresh
        </button>
      </div>
      
      <div className="text-sm space-y-1">
        {healthStatus.timestamp && (
          <div>Last checked: {new Date(healthStatus.timestamp).toLocaleTimeString()}</div>
        )}
        
        {healthStatus.database && (
          <div>Database: {healthStatus.database}</div>
        )}
        
        {healthStatus.universities_count !== null && (
          <div>Universities in database: {healthStatus.universities_count.toLocaleString()}</div>
        )}
        
        {healthStatus.error && (
          <div className="mt-2 p-2 bg-white bg-opacity-50 rounded border">
            <strong>Error:</strong> {healthStatus.error}
            <div className="mt-1 text-xs">
              Make sure the backend server is running on {BASE_URL}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ApiHealthCheck;
