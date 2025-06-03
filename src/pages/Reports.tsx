
import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { FileText, Download, Eye } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const frameworks = [
  {
    id: 'sdg',
    name: 'Sustainable Development Goals',
    description: 'UN SDG framework for global impact reporting',
    color: 'bg-blue-500'
  },
  {
    id: 'esg',
    name: 'Environmental, Social, Governance',
    description: 'ESG reporting framework for sustainability',
    color: 'bg-green-500'
  },
  {
    id: 'b_impact',
    name: 'B Impact Assessment',
    description: 'B Corp impact measurement framework',
    color: 'bg-purple-500'
  },
  {
    id: 'gri',
    name: 'Global Reporting Initiative',
    description: 'GRI sustainability reporting standards',
    color: 'bg-orange-500'
  }
];

const sampleReports = [
  {
    id: 1,
    title: 'Q2 2024 SDG Impact Report',
    framework: 'SDG',
    generated_at: '2024-06-15',
    status: 'completed'
  },
  {
    id: 2,
    title: 'ESG Performance Report',
    framework: 'ESG',
    generated_at: '2024-05-20',
    status: 'completed'
  }
];

const Reports: React.FC = () => {
  const [selectedFramework, setSelectedFramework] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const { toast } = useToast();

  const generateReport = async () => {
    if (!selectedFramework) {
      toast({
        title: 'Framework required',
        description: 'Please select a reporting framework',
        variant: 'destructive',
      });
      return;
    }

    setIsGenerating(true);
    
    // Simulate report generation
    setTimeout(() => {
      setIsGenerating(false);
      toast({
        title: 'Report generated successfully',
        description: 'Your impact report is ready for download',
      });
    }, 3000);
  };

  const downloadReport = (reportId: number) => {
    toast({
      title: 'Download started',
      description: 'Your report is being downloaded',
    });
  };

  const previewReport = (reportId: number) => {
    toast({
      title: 'Report preview',
      description: 'Opening report preview',
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
      </div>

      {/* Framework Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Generate New Report</CardTitle>
          <CardDescription>
            Choose a reporting framework to generate your impact report
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {frameworks.map((framework) => (
              <div
                key={framework.id}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  selectedFramework === framework.id
                    ? 'border-mega-primary bg-mega-primary/5'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedFramework(framework.id)}
              >
                <div className="flex items-start space-x-3">
                  <div className={`w-3 h-3 rounded-full ${framework.color} mt-1`}></div>
                  <div>
                    <h3 className="font-medium text-gray-900">{framework.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{framework.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="flex space-x-4">
            <Button
              onClick={generateReport}
              disabled={!selectedFramework || isGenerating}
              className="flex items-center space-x-2"
            >
              {isGenerating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <FileText className="h-4 w-4" />
                  <span>Generate Report</span>
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Previous Reports */}
      <Card>
        <CardHeader>
          <CardTitle>Previous Reports</CardTitle>
          <CardDescription>
            View and download your previously generated reports
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sampleReports.map((report) => (
              <div
                key={report.id}
                className="flex items-center justify-between p-4 border rounded-lg"
              >
                <div className="flex items-center space-x-4">
                  <FileText className="h-8 w-8 text-gray-400" />
                  <div>
                    <h3 className="font-medium text-gray-900">{report.title}</h3>
                    <div className="flex items-center space-x-2 mt-1">
                      <Badge variant="secondary">{report.framework}</Badge>
                      <span className="text-sm text-gray-500">
                        Generated on {new Date(report.generated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => previewReport(report.id)}
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    Preview
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => downloadReport(report.id)}
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Download
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Reports;
