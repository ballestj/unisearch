import React, { useState, useEffect } from 'react';
import { Search, Lightbulb, Globe, TrendingUp, Users, Award, BookOpen, MapPin } from 'lucide-react';

const Home = ({ onNavigate }) => {
  const [stats, setStats] = useState({ total_universities: 0, total_countries: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const BASE_URL = import.meta.env.VITE_API_BASE_URL;
        const response = await fetch(`${BASE_URL}/api/stats`); // ✅ FIXED: added response =

        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const handleStartSearching = () => {
    onNavigate('search');
  };

  const handleGetRecommendations = () => {
    onNavigate('recommendations');
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 animate-fade-in">
            Find Your Perfect{' '}
            <span className="text-yellow-400">University Exchange</span>
          </h1>
          
          <p className="text-xl md:text-2xl mb-12 text-blue-100 max-w-4xl mx-auto">
            Discover your ideal study abroad destination with AI-powered recommendations,
            comprehensive university data, and personalized matching from {stats.total_countries}+ countries.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={handleStartSearching}
              className="bg-white text-blue-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-blue-50 transition-all duration-300 transform hover:scale-105 flex items-center gap-2 shadow-lg"
            >
              <Search className="h-5 w-5" />
              Start Searching
            </button>
            
            <button
              onClick={handleGetRecommendations}
              className="bg-blue-500 bg-opacity-30 backdrop-blur-sm border border-blue-300 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-opacity-40 transition-all duration-300 transform hover:scale-105 flex items-center gap-2"
            >
              <Lightbulb className="h-5 w-5" />
              Get Recommendations
            </button>
          </div>
          
          {!loading && (
            <div className="mt-12 text-blue-200">
              <p className="text-lg">
                🌍 {stats.total_universities.toLocaleString()}+ Universities • {stats.total_countries}+ Countries • Real Student Reviews
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Why Choose UniSearch */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Choose UniSearch?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our intelligent platform combines comprehensive data with personalized
              insights to help you make the best decision for your academic future.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard
              icon={<Search className="h-8 w-8 text-blue-600" />}
              title="Advanced Search"
              description="Find universities with sophisticated filtering by rankings, costs, climate, and more."
              color="blue"
            />
            
            <FeatureCard
              icon={<Lightbulb className="h-8 w-8 text-green-600" />}
              title="AI Recommendations"
              description="Get personalized university suggestions based on your academic goals and preferences."
              color="green"
            />
            
            <FeatureCard
              icon={<Globe className="h-8 w-8 text-purple-600" />}
              title="Global Coverage"
              description="Explore universities from 80+ countries with detailed exchange program information."
              color="purple"
            />
            
            <FeatureCard
              icon={<TrendingUp className="h-8 w-8 text-orange-600" />}
              title="Multi-Source Rankings"
              description="Compare data from QS, Times Higher Education, and other authoritative sources."
              color="orange"
            />
          </div>
        </div>
      </section>

      {/* Statistics Section */}
      <section className="py-16 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <StatCard
              icon={<BookOpen className="h-12 w-12 text-blue-600 mx-auto mb-4" />}
              number={loading ? "..." : stats.total_universities.toLocaleString()}
              label="Universities"
              description="Comprehensive database of global institutions"
            />
            
            <StatCard
              icon={<MapPin className="h-12 w-12 text-green-600 mx-auto mb-4" />}
              number={loading ? "..." : `${stats.total_countries}+`}
              label="Countries"
              description="Study destinations worldwide"
            />
            
            <StatCard
              icon={<Users className="h-12 w-12 text-purple-600 mx-auto mb-4" />}
              number="45+"
              label="Student Reviews"
              description="Real feedback from exchange students"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-indigo-600 to-purple-700 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Find Your Perfect Match?
          </h2>
          <p className="text-xl text-indigo-100 mb-8">
            Start your journey to an amazing study abroad experience today.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleStartSearching}
              className="bg-white text-indigo-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-50 transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              Explore Universities
            </button>
            
            <button
              onClick={() => onNavigate('about')}
              className="border-2 border-white text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white hover:text-indigo-600 transition-all duration-300"
            >
              Learn More
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

const FeatureCard = ({ icon, title, description, color }) => {
  const colorClasses = {
    blue: 'bg-blue-50 hover:bg-blue-100',
    green: 'bg-green-50 hover:bg-green-100',
    purple: 'bg-purple-50 hover:bg-purple-100',
    orange: 'bg-orange-50 hover:bg-orange-100'
  };

  return (
    <div className={`p-6 rounded-xl ${colorClasses[color]} transition-all duration-300 hover:transform hover:scale-105 cursor-pointer`}>
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-3">{title}</h3>
      <p className="text-gray-600 leading-relaxed">{description}</p>
    </div>
  );
};

const StatCard = ({ icon, number, label, description }) => (
  <div className="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-shadow duration-300">
    {icon}
    <h3 className="text-4xl font-bold text-gray-900 mb-2">{number}</h3>
    <h4 className="text-xl font-semibold text-gray-700 mb-2">{label}</h4>
    <p className="text-gray-600">{description}</p>
  </div>
);

export default Home;
