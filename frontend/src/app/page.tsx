'use client';

import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          backgroundRepeat: 'repeat'
        }}></div>
      </div>
      
      {/* Floating Elements */}
      <div className="absolute top-20 left-20 w-16 h-16 bg-white/10 rounded-full animate-bounce-gentle"></div>
      <div className="absolute top-40 right-32 w-12 h-12 bg-white/10 rounded-full animate-bounce-gentle" style={{animationDelay: '1s'}}></div>
      <div className="absolute bottom-32 left-32 w-20 h-20 bg-white/10 rounded-full animate-bounce-gentle" style={{animationDelay: '2s'}}></div>
      <div className="absolute bottom-20 right-20 w-14 h-14 bg-white/10 rounded-full animate-bounce-gentle" style={{animationDelay: '0.5s'}}></div>
      
      <div className="max-w-4xl w-full space-y-8 text-center relative z-10">
        {/* Header */}
        <div className="animate-fade-in">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-white/20 backdrop-blur-sm rounded-3xl mb-6 animate-scale-in">
            <span className="text-5xl">🎓</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            IELTS Master Platform
          </h1>
          <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
            AI-powered IELTS writing assessment with intelligent feedback, 
            personalized learning, and comprehensive analytics.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-slide-up">
          <Link href="/auth/login" className="btn-primary btn-lg group">
            Get Started
            <svg className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
          <Link href="/test" className="btn-secondary btn-lg">
            Test Page
          </Link>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 animate-slide-up">
          <div className="glass-effect rounded-2xl p-6">
            <div className="text-3xl mb-3">🤖</div>
            <h3 className="text-lg font-semibold text-white mb-2">AI-Powered Assessment</h3>
            <p className="text-white/80 text-sm">Advanced ML models trained on 47,000+ essays</p>
          </div>
          <div className="glass-effect rounded-2xl p-6">
            <div className="text-3xl mb-3">📊</div>
            <h3 className="text-lg font-semibold text-white mb-2">Smart Analytics</h3>
            <p className="text-white/80 text-sm">Track progress with detailed insights</p>
          </div>
          <div className="glass-effect rounded-2xl p-6">
            <div className="text-3xl mb-3">🎯</div>
            <h3 className="text-lg font-semibold text-white mb-2">Personalized Learning</h3>
            <p className="text-white/80 text-sm">Adaptive learning paths for your goals</p>
          </div>
        </div>
      </div>
    </div>
  );
}
