import React, { useState, useEffect } from 'react';
import { ArrowLeft, MapPin, Trophy, Users, Star, Shield, Home, BookOpen, Calendar, Globe, Loader2 } from 'lucide-react';

const UniversityDetail = ({ universityId, onNavigate }) => {
  const [university, setUniversity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (universityId) {
      fetchUniversityDetails();
    }
  }, [universityId]);

  const fetchUniversityDetails = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/universities/${universityId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('University not found');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setUniversity(data);
    } catch (error) {
      console.error('Error fetching university details:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <button
            onClick={() => onNavigate('search')}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-6"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Search
          </button>
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            <span className="ml-2 text-gray-600">Loading university details...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <button
            onClick={() => onNavigate('search')}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-6"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Search
          </button>
          <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
            <h2 className="text-xl font-semibold text-red-800 mb-2">Error Loading University</h2>
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={fetchUniversityDetails}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!university) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <button
            onClick={() => onNavigate('search')}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-6"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Search
          </button>
          <div className="text-center py-20">
            <h2 className="text-xl font-semibold text-gray-800 mb-2">University Not Found</h2>
            <p className="text-gray-600">The requested university could not be found.</p>
          </div>
        </div>
      </div>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 4) return 'text-green-600 bg-green-100';
    if (score >= 3) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreBadgeColor = (score) => {
    if (score >= 4) return 'bg-green-600';
    if (score >= 3) return 'bg-yellow-600';
    return 'bg-red-600';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <button
            onClick={() => onNavigate('search')}
            className="flex items-center gap-2 text-white hover:text-blue-100 mb-6"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Search
          </button>
          
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div className="flex-1">
              <h1 className="text-4xl md:text-5xl font-bold mb-4">{university.name}</h1>
              <div className="flex items-center text-lg mb-4">
                <MapPin className="h-5 w-5 mr-2" />
                <span>
                  {university.city && university.country 
                    ? `${university.city}, ${university.country}`
                    : university.country || 'Location not specified'
                  }
                </span>
              </div>
              {university.qs_rank && (
                <div className="inline-flex items-center bg-white bg-opacity-20 rounded-lg px-4 py-2">
                  <Trophy className="h-5 w-5 mr-2" />
                  <span className="font-semibold">QS World Ranking #{university.qs_rank}</span>
                </div>
              )}
            </div>
            
            {/* Quick Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Academic', value: university.academic_rigor, icon: Trophy },
                { label: 'Diversity', value: university.cultural_diversity, icon: Users },
                { label: 'Student Life', value: university.student_life, icon: Star },
                { label: 'Safety', value: university.campus_safety, icon: Shield }
              ].map(({ label, value, icon: Icon }) => (
                <div key={label} className="bg-white bg-opacity-10 rounded-lg p-4 text-center">
                  <Icon className="h-6 w-6 mx-auto mb-2 opacity-80" />
                  <div className="text-sm opacity-80">{label}</div>
                  {value ? (
                    <div className="text-2xl font-bold">{value.toFixed(1)}</div>
                  ) : (
                    <div className="text-sm opacity-60">N/A</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* University Overview */}
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <BookOpen className="h-6 w-6 text-blue-600" />
                University Overview
              </h2>
              
              <div className="prose prose-gray max-w-none">
                <p className="text-gray-600 leading-relaxed mb-6">
                  {university.name} is a prestigious institution known for its academic excellence and diverse student body. 
                  The university offers a wide range of programs and has established itself as a leading educational institution
                  {university.country ? ` in ${university.country}` : ''}.
                </p>
              </div>

              {/* Quality Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                {[
                  { 
                    label: 'Academic Rigor', 
                    value: university.academic_rigor, 
                    icon: Trophy,
                    description: 'Quality of education and academic standards'
                  },
                  { 
                    label: 'Cultural Diversity', 
                    value: university.cultural_diversity, 
                    icon: Users,
                    description: 'International student presence and multicultural environment'
                  },
                  { 
                    label: 'Student Life', 
                    value: university.student_life, 
                    icon: Star,
                    description: 'Campus activities and social opportunities'
                  },
                  { 
                    label: 'Campus Safety', 
                    value: university.campus_safety, 
                    icon: Shield,
                    description: 'Security measures and overall safety'
                  }
                ].map(({ label, value, icon: Icon, description }) => (
                  <div key={label} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Icon className="h-5 w-5 text-gray-600" />
                        <span className="font-semibold text-gray-900">{label}</span>
                      </div>
                      {value ? (
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(value)}`}>
                          {value.toFixed(1)}/5.0
                        </span>
                      ) : (
                        <span className="text-sm text-gray-400">Not rated</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">{description}</p>
                    {value && (
                      <div className="mt-3">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${getScoreBadgeColor(value)}`}
                            style={{ width: `${(value / 5) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Additional Information */}
            <div className="bg-white rounded-xl shadow-sm p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <Globe className="h-6 w-6 text-blue-600" />
                Additional Information
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  { label: 'Language of Instruction', value: university.language, icon: Globe },
                  { label: 'Accommodation', value: university.accommodation, icon: Home },
                  { label: 'Language Classes', value: university.language_classes, icon: BookOpen },
                  { label: 'Accessibility Support', value: university.accessibility, icon: Users }
                ].map(({ label, value, icon: Icon }) => (
                  <div key={label} className="flex items-start gap-3">
                    <Icon className="h-5 w-5 text-gray-600 mt-0.5" />
                    <div>
                      <h3 className="font-semibold text-gray-900">{label}</h3>
                      <p className="text-gray-600 text-sm">
                        {value || 'Information not available'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            
            {/* Quick Facts */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Facts</h3>
              
              <div className="space-y-4">
                {university.qs_rank && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Trophy className="h-4 w-4 text-yellow-600" />
                      <span className="text-gray-700">QS Ranking</span>
                    </div>
                    <span className="font-semibold text-gray-900">#{university.qs_rank}</span>
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-blue-600" />
                    <span className="text-gray-700">Location</span>
                  </div>
                  <span className="font-semibold text-gray-900 text-right">
                    {university.city && university.country 
                      ? `${university.city}, ${university.country}`
                      : university.country || 'Not specified'
                    }
                  </span>
                </div>

                {university.overall_quality && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Star className="h-4 w-4 text-purple-600" />
                      <span className="text-gray-700">Overall Quality</span>
                    </div>
                    <span className="font-semibold text-gray-900">{university.overall_quality.toFixed(1)}/5.0</span>
                  </div>
                )}

                {university.response_count > 0 && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-green-600" />
                      <span className="text-gray-700">Student Reviews</span>
                    </div>
                    <span className="font-semibold text-gray-900">{university.response_count}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Student Reviews */}
            {university.response_count > 0 && (
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Student Feedback</h3>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Users className="h-5 w-5 text-blue-600" />
                    <span className="font-semibold text-blue-800">
                      {university.response_count} Student{university.response_count !== 1 ? 's' : ''} Reviewed
                    </span>
                  </div>
                  <p className="text-blue-700 text-sm">
                    This university has been reviewed by actual exchange students, 
                    providing you with real insights into the academic and social experience.
                  </p>
                </div>
              </div>
            )}

            {/* Call to Action */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
              <h3 className="text-lg font-semibold mb-3">Interested in This University?</h3>
              <p className="text-blue-100 text-sm mb-4">
                Get more information about exchange programs and application requirements.
              </p>
              <div className="space-y-2">
                <button 
                  onClick={() => onNavigate('search')}
                  className="w-full bg-white text-blue-600 font-semibold py-2 px-4 rounded-lg hover:bg-gray-100 transition-colors text-sm"
                >
                  Find Similar Universities
                </button>
                <button 
                  onClick={() => onNavigate('recommendations')}
                  className="w-full border border-white text-white font-semibold py-2 px-4 rounded-lg hover:bg-white hover:text-blue-600 transition-colors text-sm"
                >
                  Get Recommendations
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UniversityDetail;