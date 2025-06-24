import React, { useEffect, useState } from 'react';
import Navbar from './components/Navbar';
import ApiHealthCheck from './components/ApiHealthCheck';
import Home from './pages/Home';
import SearchPage from './pages/SearchPage';
import Recommendations from './pages/Recommendations';
import UniversityDetail from './pages/UniversityDetail';
import About from './pages/About';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedUniversityId, setSelectedUniversityId] = useState(null);
  const [showHealthCheck, setShowHealthCheck] = useState(false);

  // 🔍 Health Check on First Load
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/health`);
        const data = await response.json();
        console.log("✅ API Health:", data);
      } catch (err) {
        console.error("❌ Failed to connect to API:", err);
      }
    };
    checkHealth();
  }, []);

  const renderPage = () => {
    try {
      switch (currentPage) {
        case 'home':
          return <Home onNavigate={setCurrentPage} />;
        case 'search':
          return (
            <SearchPage
              onNavigate={setCurrentPage}
              onSelectUniversity={(id) => {
                setSelectedUniversityId(id);
                setCurrentPage('university');
              }}
            />
          );
        case 'recommendations':
          return (
            <Recommendations
              onNavigate={setCurrentPage}
              onSelectUniversity={(id) => {
                setSelectedUniversityId(id);
                setCurrentPage('university');
              }}
            />
          );
        case 'university':
          return (
            <UniversityDetail
              universityId={selectedUniversityId}
              onNavigate={setCurrentPage}
            />
          );
        case 'about':
          return <About onNavigate={setCurrentPage} />;
        default:
          return <Home onNavigate={setCurrentPage} />;
      }
    } catch (error) {
      // ERROR BOUNDARY
      return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded">
            <h2 className="font-bold">Error loading page</h2>
            <p>{error.message}</p>
            <button 
              onClick={() => setCurrentPage('home')}
              className="mt-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Go to Home
            </button>
          </div>
        </div>
      );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar currentPage={currentPage} onNavigate={setCurrentPage} />
      
      {/* Health Check Toggle */}
      <div className="bg-gray-100 border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
          <button
            onClick={() => setShowHealthCheck(!showHealthCheck)}
            className="text-xs text-gray-600 hover:text-gray-800"
          >
            {showHealthCheck ? 'Hide' : 'Show'} API Status
          </button>
        </div>
      </div>

      {/* Health Check Component with Fallback */}
      {showHealthCheck && (
        <div className="bg-gray-100 border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <React.Suspense 
              fallback={
                <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-4 rounded">
                  Loading API Health Check...
                </div>
              }
            >
              <ApiHealthCheck />
            </React.Suspense>
          </div>
        </div>
      )}

      {renderPage()}
    </div>
  );
}

export default App;
