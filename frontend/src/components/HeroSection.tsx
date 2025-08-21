
import { Button } from '@/components/ui/button';
import { ArrowDown } from 'lucide-react';

const HeroSection = () => {
  return (
    <section className="relative bg-gradient-to-br from-white via-gray-50 to-mega-primary/5 py-20 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-mega-dark mb-6 animate-fade-in-up">
            AI-Powered Impact Reporting for{' '}
            <span className="text-mega-primary">Social Enterprises</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto animate-fade-in-up [animation-delay:200ms]">
            Automate impact reporting, generate interactive dashboards, and intelligently connect 
            with aligned funders. Empower your mission with cutting-edge AI tools.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12 animate-fade-in-up [animation-delay:400ms]">
            <Button 
              size="lg" 
              className="bg-mega-primary hover:bg-mega-primary/90 text-white px-8 py-3 text-lg"
            >
              Start Free Trial
            </Button>
            <Button 
              variant="outline" 
              size="lg" 
              className="border-mega-primary text-mega-primary hover:bg-mega-primary hover:text-white px-8 py-3 text-lg"
            >
              Watch Demo
            </Button>
          </div>

          {/* Key Benefits */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16 animate-fade-in-up [animation-delay:600ms]">
            <div className="text-center">
              <div className="w-16 h-16 bg-mega-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">📊</span>
              </div>
              <h3 className="text-lg font-semibold text-mega-dark mb-2">Automated Dashboards</h3>
              <p className="text-gray-600">Generate interactive impact dashboards with AI-powered insights</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-mega-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🎯</span>
              </div>
              <h3 className="text-lg font-semibold text-mega-dark mb-2">SDG Alignment</h3>
              <p className="text-gray-600">Automatically map your impact to UN Sustainable Development Goals</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-mega-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🤝</span>
              </div>
              <h3 className="text-lg font-semibold text-mega-dark mb-2">Investor Matching</h3>
              <p className="text-gray-600">Connect with mission-aligned funders through intelligent matching</p>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <ArrowDown className="text-mega-primary" size={24} />
      </div>
    </section>
  );
};

export default HeroSection;
