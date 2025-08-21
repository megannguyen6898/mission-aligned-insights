
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const DashboardPreview = () => {
  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-mega-primary/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold text-mega-dark mb-4">
            See Your Impact Come to <span className="text-mega-primary">Life</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Transform raw data into compelling visual stories that showcase your organization's true impact.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          {/* Dashboard Mock */}
          <div className="space-y-6">
            <Card className="border-mega-primary/20 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="text-mega-dark">Impact Overview</span>
                  <span className="text-sm text-mega-primary font-normal">Live Data</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="text-center p-4 bg-mega-primary/10 rounded-lg">
                    <div className="text-2xl font-bold text-mega-primary">2,547</div>
                    <div className="text-sm text-gray-600">Lives Impacted</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">89%</div>
                    <div className="text-sm text-gray-600">SDG Alignment</div>
                  </div>
                </div>
                
                {/* Mock Chart */}
                <div className="h-32 bg-gradient-to-r from-mega-primary/20 to-mega-primary/5 rounded-lg flex items-end justify-center space-x-2 p-4">
                  <div className="w-8 bg-mega-primary/60 rounded-t" style={{ height: '60%' }}></div>
                  <div className="w-8 bg-mega-primary/80 rounded-t" style={{ height: '80%' }}></div>
                  <div className="w-8 bg-mega-primary rounded-t" style={{ height: '100%' }}></div>
                  <div className="w-8 bg-mega-primary/70 rounded-t" style={{ height: '70%' }}></div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-gray-200 shadow-md">
              <CardHeader>
                <CardTitle className="text-mega-dark">SDG Impact Meter</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">🎯 Goal 1: No Poverty</span>
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div className="bg-mega-primary h-2 rounded-full" style={{ width: '85%' }}></div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">🏥 Goal 3: Good Health</span>
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div className="bg-mega-primary h-2 rounded-full" style={{ width: '72%' }}></div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">📚 Goal 4: Education</span>
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div className="bg-mega-primary h-2 rounded-full" style={{ width: '90%' }}></div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Features List */}
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-mega-primary rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-white text-sm">✓</span>
                </div>
                <div>
                  <h3 className="font-semibold text-mega-dark mb-1">Real-time Data Visualization</h3>
                  <p className="text-gray-600">Charts and metrics update automatically as you add new data</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-mega-primary rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-white text-sm">✓</span>
                </div>
                <div>
                  <h3 className="font-semibold text-mega-dark mb-1">Interactive Filtering</h3>
                  <p className="text-gray-600">Filter by date, geography, program, or any custom dimension</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-mega-primary rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-white text-sm">✓</span>
                </div>
                <div>
                  <h3 className="font-semibold text-mega-dark mb-1">Journey Maps & Ripple Effects</h3>
                  <p className="text-gray-600">Visualize impact pathways from inputs to long-term outcomes</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-mega-primary rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-white text-sm">✓</span>
                </div>
                <div>
                  <h3 className="font-semibold text-mega-dark mb-1">Framework Alignment</h3>
                  <p className="text-gray-600">Automatic mapping to SDGs, ESG metrics, and B Impact standards</p>
                </div>
              </div>
            </div>

            <Button className="w-full bg-mega-primary hover:bg-mega-primary/90 text-white">
              Try Dashboard Demo
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DashboardPreview;
