import React from 'react';
import { Users, Database, Zap, Shield, ArrowLeft } from 'lucide-react';

const About = ({ onNavigate }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <button
            onClick={() => onNavigate('home')}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </button>
          <h1 className="text-4xl font-bold text-gray-900">About UniSearch</h1>
          <p className="text-xl text-gray-600 mt-4">
            Your intelligent companion for finding the perfect university exchange program
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Mission Section */}
        <div className="bg-white rounded-xl shadow-sm p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Mission</h2>
          <p className="text-lg text-gray-700 leading-relaxed mb-6">
            UniSearch was created to solve a fundamental problem: finding the right university for your exchange program 
            is incredibly difficult and time-consuming. Traditional search methods are fragmented, outdated, and don't 
            provide personalized insights.
          </p>
          <p className="text-lg text-gray-700 leading-relaxed">
            We combine comprehensive data from multiple authoritative sources with real student feedback and AI-powered 
            recommendations to help you make the best decision for your academic future.
          </p>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-xl shadow-sm p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">How UniSearch Works</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FeatureStep
              icon={<Database className="h-8 w-8 text-blue-600" />}
              title="Data Integration"
              description="We aggregate data from QS World Rankings, Times Higher Education, and other trusted sources"
              step="1"
            />
            
            <FeatureStep
              icon={<Users className="h-8 w-8 text-green-600" />}
              title="Student Feedback"
              description="Real reviews and ratings from students who have actually studied at these universities"
              step="2"
            />
            
            <FeatureStep
              icon={<Zap className="h-8 w-8 text-purple-600" />}
              title="AI Matching"
              description="Our recommendation engine analyzes your preferences to suggest the best matches"
              step="3"
            />
            
            <FeatureStep
              icon={<Shield className="h-8 w-8 text-orange-600" />}
              title="Verified Results"
              description="All data is cross-verified and regularly updated to ensure accuracy and reliability"
              step="4"
            />
          </div>
        </div>

        {/* Features */}
        <div className="bg-white rounded-xl shadow-sm p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Key Features</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">🔍 Advanced Search</h3>
              <ul className="space-y-2 text-gray-700">
                <li>• Filter by country, ranking, academic rigor</li>
                <li>• Search by specific criteria like language or safety</li>
                <li>• Real-time results with pagination</li>
                <li>• Smart fuzzy matching for university names</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">🤖 AI Recommendations</h3>
              <ul className="space-y-2 text-gray-700">
                <li>• Personalized suggestions based on your goals</li>
                <li>• Weighted scoring algorithm</li>
                <li>• Consider academic and lifestyle preferences</li>
                <li>• Match percentage for each recommendation</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">📊 Comprehensive Data</h3>
              <ul className="space-y-2 text-gray-700">
                <li>• 1,496+ universities from 80+ countries</li>
                <li>• QS World University Rankings integration</li>
                <li>• Student life and safety ratings</li>
                <li>• Accommodation and language information</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">👥 Real Student Reviews</h3>
              <ul className="space-y-2 text-gray-700">
                <li>• 45+ verified student responses</li>
                <li>• Ratings for academic rigor and campus life</li>
                <li>• Cultural diversity insights</li>
                <li>• Safety and accessibility information</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Technology */}
        <div className="bg-white rounded-xl shadow-sm p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Technology Stack</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Backend</h3>
              <ul className="space-y-2 text-gray-700">
                <li>• <strong>FastAPI:</strong> Modern Python web framework</li>
                <li>• <strong>SQLite:</strong> Efficient database storage</li>
                <li>• <strong>Google Sheets API:</strong> Real-time data sync</li>
                <li>• <strong>Fuzzy Matching:</strong> Intelligent university name matching</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Frontend</h3>
              <ul className="space-y-2 text-gray-700">
                <li>• <strong>React 18:</strong> Modern user interface</li>
                <li>• <strong>Tailwind CSS:</strong> Beautiful, responsive design</li>
                <li>• <strong>Vite:</strong> Fast development and building</li>
                <li>• <strong>Lucide Icons:</strong> Consistent iconography</li>
              </ul>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 text-white text-center mt-8">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Your Journey?</h2>
          <p className="text-xl text-blue-100 mb-6">
            Join thousands of students who have found their perfect study abroad match
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => onNavigate('search')}
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Start Searching
            </button>
            <button
              onClick={() => onNavigate('recommendations')}
              className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
            >
              Get Recommendations
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const FeatureStep = ({ icon, title, description, step }) => (
  <div className="relative text-center">
    <div className="bg-gray-50 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
      {icon}
    </div>
    <div className="absolute -top-2 -right-2 bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">
      {step}
    </div>
    <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
    <p className="text-gray-600 text-sm">{description}</p>
  </div>
);

export default About;