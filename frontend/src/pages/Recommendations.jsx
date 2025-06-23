import React, { useState, useEffect } from 'react';
import { Lightbulb, Sliders, Search, Trophy, Users, Star, MapPin, ChevronRight, ArrowLeft, Loader2 } from 'lucide-react';

const Recommendations = ({ onNavigate, onSelectUniversity }) => {
  const [step, setStep] = useState(1);
  const [preferences, setPreferences] = useState({
    academic_importance: 3,
    diversity_importance: 3,
    student_life_importance: 3,
    preferred_countries: [],
    max_ranking: ''
  });
  const [countries, setCountries] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const BASE_URL = import.meta.env.VITE_API_BASE_URL;

  useEffect(() => {
    fetchCountries();
  }, []);

  const fetchCountries = async () => {
    try {
      const response = await fetch(`${BASE_URL}/api/countries`);
      if (response.ok) {
        const data = await response.json();
        setCountries(data.slice(0, 20)); // Show top 20 countries
      }
    } catch (error) {
      console.error('Error fetching countries:', error);
    }
  };

  const getRecommendations = async () => {
    setLoading(true);
    try {
      const requestData = {
        academic_importance: preferences.academic_importance,
        diversity_importance: preferences.diversity_importance,
        student_life_importance: preferences.student_life_importance,
        preferred_countries: preferences.preferred_countries.length > 0 ? preferences.preferred_countries : null,
        max_ranking: preferences.max_ranking ? parseInt(preferences.max_ranking) : null
      };

      const response = await fetch(`${BASE_URL}/api/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data);
        setStep(3);
      }
    } catch (error) {
      console.error('Error getting recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCountryToggle = (countryName) => {
    setPreferences(prev => ({
      ...prev,
      preferred_countries: prev.preferred_countries.includes(countryName)
        ? prev.preferred_countries.filter(c => c !== countryName)
        : [...prev.preferred_countries, countryName]
    }));
  };

  const handleSliderChange = (key, value) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const getScoreColor = (score) => {
    if (score >= 4) return 'text-green-600 bg-green-100';
    if (score >= 3) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => step === 1 ? onNavigate('home') : setStep(step - 1)}
              className="flex items-center gap-2 text-blue-600 hover:text-blue-700"
            >
              <ArrowLeft className="h-4 w-4" />
              {step === 1 ? 'Back to Home' : 'Previous Step'}
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                <Lightbulb className="h-8 w-8 text-yellow-500" />
                AI Recommendations
              </h1>
              <p className="text-gray-600 mt-1">Get personalized university suggestions based on your preferences</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Step 1: Preferences */}
        {step === 1 && (
          <div className="bg-white rounded-xl shadow-sm p-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Tell us about your priorities</h2>
              <p className="text-gray-600">Rate how important these factors are to you (1 = Not Important, 5 = Very Important)</p>
            </div>

            <div className="space-y-8">
              <PreferenceSlider
                icon={<Trophy className="h-6 w-6 text-blue-600" />}
                title="Academic Excellence"
                description="University rankings, research quality, and academic reputation"
                value={preferences.academic_importance}
                onChange={(value) => handleSliderChange('academic_importance', value)}
              />

              <PreferenceSlider
                icon={<Users className="h-6 w-6 text-green-600" />}
                title="Cultural Diversity"
                description="International student body and multicultural environment"
                value={preferences.diversity_importance}
                onChange={(value) => handleSliderChange('diversity_importance', value)}
              />

              <PreferenceSlider
                icon={<Star className="h-6 w-6 text-purple-600" />}
                title="Student Life"
                description="Campus activities, social opportunities, and overall student experience"
                value={preferences.student_life_importance}
                onChange={(value) => handleSliderChange('student_life_importance', value)}
              />

              <div className="border-t pt-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Maximum QS Ranking (Optional)
                </label>
                <input
                  type="number"
                  placeholder="e.g., 500"
                  value={preferences.max_ranking}
                  onChange={(e) => handleSliderChange('max_ranking', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">Leave empty to include all rankings</p>
              </div>
            </div>

            <div className="flex justify-center mt-8">
              <button
                onClick={() => setStep(2)}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                Continue
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Country Preferences */}
        {step === 2 && (
          <div className="bg-white rounded-xl shadow-sm p-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Select preferred countries</h2>
              <p className="text-gray-600">Choose countries you'd like to study in (optional - leave empty for global recommendations)</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mb-8">
              {countries.map((country) => (
                <button
                  key={country.name}
                  onClick={() => handleCountryToggle(country.name)}
                  className={`p-3 rounded-lg border text-sm font-medium transition-all ${
                    preferences.preferred_countries.includes(country.name)
                      ? 'bg-blue-100 border-blue-300 text-blue-700'
                      : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <div className="font-semibold">{country.name}</div>
                  <div className="text-xs opacity-75">{country.count} universities</div>
                </button>
              ))}
            </div>

            {preferences.preferred_countries.length > 0 && (
              <div className="bg-blue-50 p-4 rounded-lg mb-6">
                <p className="text-sm text-blue-700">
                  <strong>Selected:</strong> {preferences.preferred_countries.join(', ')}
                </p>
              </div>
            )}

            <div className="flex justify-center gap-4">
              <button
                onClick={() => setStep(1)}
                className="px-8 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Back
              </button>
              <button
                onClick={getRecommendations}
                disabled={loading}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    Get Recommendations
                    <Lightbulb className="h-4 w-4" />
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Results */}
        {step === 3 && (
          <div>
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Your Personalized Recommendations</h2>
                  <p className="text-gray-600">Based on your preferences, here are your top university matches</p>
                </div>
                <button
                  onClick={() => setStep(1)}
                  className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
                >
                  <Sliders className="h-4 w-4" />
                  Adjust Preferences
                </button>
              </div>
            </div>

            {recommendations.length > 0 ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {recommendations.map((university, index) => (
                  <UniversityRecommendationCard
                    key={university.id}
                    university={university}
                    rank={index + 1}
                    onSelect={() => {
                      onSelectUniversity(university.id);
                      onNavigate('university');
                    }}
                  />
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm p-12 text-center">
                <Search className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No recommendations found</h3>
                <p className="text-gray-600 mb-6">Try adjusting your preferences or removing country filters</p>
                <button
                  onClick={() => setStep(1)}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  Adjust Preferences
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const PreferenceSlider = ({ icon, title, description, value, onChange }) => (
  <div className="space-y-3">
    <div className="flex items-center gap-3">
      {icon}
      <div>
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
    </div>
    <div className="flex items-center gap-4">
      <span className="text-sm text-gray-500 w-16">Not Important</span>
      <input
        type="range"
        min="1"
        max="5"
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="flex-1"
      />
      <span className="text-sm text-gray-500 w-16">Very Important</span>
      <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold w-8 text-center">
        {value}
      </div>
    </div>
  </div>
);

const UniversityRecommendationCard = ({ university, rank, onSelect }) => {
  const getScoreColor = (score) => {
    if (score >= 4) return 'text-green-600 bg-green-100';
    if (score >= 3) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-100 overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">
              #{rank}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 text-lg leading-tight">
                {university.name}
              </h3>
              <p className="text-gray-600 flex items-center gap-1 text-sm">
                <MapPin className="h-4 w-4" />
                {university.city}, {university.country}
              </p>
            </div>
          </div>
          {university.qs_rank && (
            <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded-lg text-sm font-medium">
              QS #{university.qs_rank}
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3 mb-4">
          {[
            { label: 'Academic', value: university.academic_rigor, icon: Trophy },
            { label: 'Diversity', value: university.cultural_diversity, icon: Users },
            { label: 'Student Life', value: university.student_life, icon: Star },
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
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            View Details
          </button>
        </div>
      </div>
    </div>
  );
};

export default Recommendations;
