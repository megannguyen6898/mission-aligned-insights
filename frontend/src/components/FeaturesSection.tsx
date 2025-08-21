
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const FeaturesSection = () => {
  const features = [
    {
      title: "Smart Profile Setup",
      description: "AI auto-populates organization details from web search, including mission, sector, and key goals",
      icon: "🧭",
      highlight: true
    },
    {
      title: "Seamless Data Integration",
      description: "Upload CSV/Excel files or connect directly to Xero, Google Sheets, and Google Docs",
      icon: "📁",
      highlight: false
    },
    {
      title: "Interactive Dashboards",
      description: "Dynamic visualizations with before/after comparisons, journey maps, and ripple effect tracking",
      icon: "📊",
      highlight: true
    },
    {
      title: "AI-Generated Reports",
      description: "Auto-written impact reports with framework mapping, visualizations, and stakeholder quotes",
      icon: "📑",
      highlight: false
    },
    {
      title: "Framework Alignment",
      description: "Map your data to SDG goals, ESG metrics, and B Impact standards with built-in indicators",
      icon: "🧩",
      highlight: false
    },
    {
      title: "Intelligent Investor Matching",
      description: "Get matched with aligned funders based on mission, location, SDG alignment, and performance",
      icon: "🔐",
      highlight: true
    }
  ];

  return (
    <section id="features" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold text-mega-dark mb-4">
            Everything You Need to <span className="text-mega-primary">Amplify Impact</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            From data upload to investor connections, our AI-powered platform streamlines 
            every aspect of impact reporting and funding discovery.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card 
              key={index} 
              className={`transition-all duration-300 hover:shadow-lg hover:-translate-y-1 ${
                feature.highlight ? 'border-mega-primary shadow-md' : 'border-gray-200'
              }`}
            >
              <CardHeader>
                <div className="flex items-center space-x-3">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                    feature.highlight ? 'bg-mega-primary/10' : 'bg-gray-100'
                  }`}>
                    <span className="text-2xl">{feature.icon}</span>
                  </div>
                  <CardTitle className="text-lg text-mega-dark">{feature.title}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-gray-600 leading-relaxed">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
