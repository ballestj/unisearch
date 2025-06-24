import React, { useState, useEffect, useCallback } from 'react';
import { Search, Filter, MapPin, Trophy, Users, Star, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import ApiHealthCheck from '../components/ApiHealthCheck';

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

const SearchPage = ({ onNavigate, onSelectUniversity }) => {
  const [universities, setUniversities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [countries, setCountries] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
  const [error, setError] = useState(null);
  const [showHealthCheck, setShowHealthCheck] = useState(false);
  
  // Filter states
  const [filters, setFilters] = useState({
    country: '',
    minRank: '',
    maxRank: '',
    minAcademicRigor: 0,
    minCulturalDiversity: 0,
    minStudentLife: 0,
    minCampusSafety: 0
  });

  const universitiesPerPage = 12;

  // Fetch countries for filter dropdown
  useEffect(() => {
    const fetchCountries = async () => {
      try {
        const response = await fetch(`${BASE_URL}/countries`);
        if (response.ok) {
          const data = await response.json();
          setCountries(data || []);
        } else {
          console.error('Failed to fetch countries:', response.status);
        }
      } catch (error) {
        console.error('Error fetching countries:', error);
      }
    };
    fetchCountries();
  }, []);

  // Fixed search function
  const searchUniversities = useCallback(async (query, currentFilters, page) => {
    setLoading(true);
    setError(null);
    
    try {
      const offset = (page - 1) * universitiesPerPage;
      const searchParams = new URLSearchParams({
        limit: universitiesPerPage.toString(),
        offset: offset.toString()
      });
      
      if (query?.trim()) {
        searchParams.append('search', query.trim());
      }
      if (currentFilters.country) {
        searchParams.append('country', currentFilters.country);
      }

      console.log('Searching with params:', searchParams.toString());
      
      const response = await fetch(`${BASE_URL}/universities?${searchParams}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('API Response:', data);
      
      let results = data || [];
      
      // Apply client-side filters for quality ratings
      if (currentFilters.minAcademicRigor > 0 ||
          currentFilters.minCulturalDiversity > 0 ||
          currentFilters.minStudentLife > 0 ||
          currentFilters.minCampusSafety > 0 ||
          currentFilters.minRank ||
          currentFilters.maxRank) {
        
        results = results.filter(uni => {
          const academicMatch = (uni.academic_rigor || 0) >= currentFilters.minAcademicRigor;
          const diversityMatch = (uni.cultural_diversity || 0) >= currentFilters.minCulturalDiversity;
          const studentLifeMatch = (uni.student_life || 0) >= currentFilters.minStudentLife;
          const safetyMatch = (uni.campus_safety || 0) >= currentFilters.minCampusSafety;
          
          let rankMatch = true;
          if (currentFilters.minRank || currentFilters.maxRank) {
            const rank = uni.qs_rank;
            if (rank) {
              if (currentFilters.minRank && rank < parseInt(currentFilters.minRank)) rankMatch = false;
              if (currentFilters.maxRank && rank > parseInt(currentFilters.maxRank)) rankMatch = false;
            } else if (currentFilters.minRank || currentFilters.maxRank) {
              rankMatch = false; // Exclude unranked universities if rank filter is applied
            }
          }
          
          return academicMatch && diversityMatch && studentLifeMatch && safetyMatch && rankMatch;
        });
      }
      
      setUniversities(results);
      setTotalResults(results.length);
      
    } catch (error) {
      console.error('Error searching universities:', error);
      setError(error.message);
      setUniversities([]);
      setTotalResults(0);
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounce function
  const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  };

  const debouncedSearch = useCallback(debounce(searchUniversities, 500), [searchUniversities]);

  // Initial load and search when dependencies change
  useEffect(() => {
    debouncedSearch(searchQuery, filters, currentPage);
  }, [searchQuery, filters, currentPage, debouncedSearch]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1); // Reset to first page when filters change
  };

  const clearFilters = () => {
    setFilters({
      country: '',
      minRank: '',
      maxRank: '',
      minAcademicRigor: 0,
      minCulturalDiversity: 0,
      minStudentLife: 0,
      minCampusSafety: 0
    });
    setSearchQuery('');
    setCurrentPage(1);
  };

  const totalPages = Math.ceil(totalResults / universitiesPerPage);
  const startIndex = (currentPage - 1) * universitiesPerPage;
  const currentUniversities = universities.slice(startIndex, startIndex + universitiesPerPage);

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Find Your Perfect University</h1>
              <p className="text-gray-600 mt-1">
                Search through {totalResults > 0 ? totalResults.toLocaleString() : '1,496'} universities worldwide
              </p>
            </div>
            
            {/* Search Bar */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                placeholder="Search universities, cities, or countries..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>
      </div>

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

      {/* Health Check Component */}
      {showHealthCheck && (
        <div className="bg-gray-100 border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <ApiHealthCheck />
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <div className="lg:w-80">
            <div className="bg-white rounded-xl shadow-sm p-6 sticky top-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Filter className="h-5 w-5" />
                  Filters
                </h3>
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="lg:hidden text-blue-600 hover:text-blue-700"
                >
                  {showFilters ? 'Hide' : 'Show'}
                </button>
              </div>
              
              <div className={`space-y-6 ${showFilters ? 'block' : 'hidden lg:block'}`}>
                {/* Country Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Country</label>
                  <select
                    value={filters.country}
                    onChange={(e) => handleFilterChange('country', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Countries</option>
                    {countries.map(country => (
                      <option key={country.name} value={country.name}>
                        {country.name} ({country.count})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Ranking Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">QS World Ranking</label>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="number"
                      placeholder="Min rank"
                      value={filters.minRank}
                      onChange={(e) => handleFilterChange('minRank', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <input
                      type="number"
                      placeholder="Max rank"
                      value={filters.maxRank}
                      onChange={(e) => handleFilterChange('maxRank', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Quality Filters */}
                {[
                  { key: 'minAcademicRigor', label: 'Academic Rigor', icon: Trophy },
                  { key: 'minCulturalDiversity', label: 'Cultural Diversity', icon: Users },
                  { key: 'minStudentLife', label: 'Student Life', icon: Star },
                  { key: 'minCampusSafety', label: 'Campus Safety', icon: MapPin }
                ].map(({ key, label, icon: Icon }) => (
                  <div key={key}>
                    <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                      <Icon className="h-4 w-4" />
                      {label} (Min: {filters[key]}/5)
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="5"
                      step="0.5"
                      value={filters[key]}
                      onChange={(e) => handleFilterChange(key, parseFloat(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>0</span>
                      <span>5</span>
                    </div>
                  </div>
                ))}

                <button
                  onClick={clearFilters}
                  className="w-full py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Clear All Filters
                </button>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="flex-1">
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-600">
                {loading ? 'Searching...' : `Showing ${currentUniversities.length} of ${totalResults} universities`}
              </p>
              {totalPages > 1 && (
                <p className="text-sm text-gray-500">
                  Page {currentPage} of {totalPages}
                </p>
              )}
            </div>

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <p className="text-red-700">Error: {error}</p>
                <button
                  onClick={() => {
                    setError(null);
                    searchUniversities(searchQuery, filters, currentPage);
                  }}
                  className="text-red-600 hover:text-red-700 font-medium mt-2"
                >
                  Try Again
                </button>
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                <span className="ml-2 text-gray-600">Searching universities...</span>
              </div>
            )}

            {/* University Grid */}
            {!loading && !error && currentUniversities.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {currentUniversities.map((university) => (
                  <UniversityCard 
                    key={university.id} 
                    university={university} 
                    onSelect={() => {
                      onSelectUniversity(university.id);
                      onNavigate('university');
                    }}
                  />
                ))}
              </div>
            )}

            {/* No Results */}
            {!loading && !error && currentUniversities.length === 0 && (
              <div className="text-center py-12">
                <Search className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No universities found</h3>
                <p className="text-gray-600 mb-4">Try adjusting your search criteria or filters</p>
                <button
                  onClick={clearFilters}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  Clear All Filters
                </button>
              </div>
            )}

            {/* Pagination */}
            {!loading && !error && totalPages > 1 && (
              <div className="flex items-center justify-center space-x-2 mt-8">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="p-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                
                {[...Array(Math.min(5, totalPages))].map((_, i) => {
                  const page = currentPage <= 3 ? i + 1 : currentPage - 2 + i;
                  if (page > totalPages) return null;
                  
                  return (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`px-4 py-2 rounded-lg border ${
                        page === currentPage
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      {page}
                    </button>
                  );
                })}
                
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="p-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// University Card Component
const UniversityCard = ({ university, onSelect }) => {
  const getScoreColor = (score) => {
    if (score >= 4) return 'text-green-600 bg-green-100';
    if (score >= 3) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-100 overflow-hidden">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 text-lg leading-tight mb-1">
              {university.name}
            </h3>
            <p className="text-gray-600 flex items-center gap-1 text-sm">
              <MapPin className="h-4 w-4" />
              {university.city && university.country ? `${university.city}, ${university.country}` : university.country || 'Location not specified'}
            </p>
          </div>
          {university.qs_rank && (
            <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded-lg text-sm font-medium">
              #{university.qs_rank}
            </div>
          )}
        </div>

        {/* Quality Scores */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          {[
            { label: 'Academic', value: university.academic_rigor, icon: Trophy },
            { label: 'Diversity', value: university.cultural_diversity, icon: Users },
            { label: 'Life', value: university.student_life, icon: Star },
            { label: 'Safety', value: university.campus_safety, icon: MapPin }
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <Icon className="h-3 w-3 text-gray-500" />
                <span className="text-xs text-gray-600">{label}</span>
              </div>
              {value ? (
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getScoreColor(value)}`}>
                  {value.toFixed(1)}
                </span>
              ) : (
                <span className="text-xs text-gray-400">N/A</span>
              )}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          {university.response_count > 0 ? (
            <span className="text-xs text-gray-500">
              {university.response_count} student reviews
            </span>
          ) : (
            <span className="text-xs text-gray-400">No reviews yet</span>
          )}
          <button
            onClick={onSelect}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            View Details →
          </button>
        </div>
      </div>
    </div>
  );
};

export default SearchPage;