
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Upload as UploadIcon, FileText, Database, Sheet } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { dataService } from '../services/data.service';
import { dashboardService } from '../services/dashboard.service';

const Upload: React.FC = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    setIsUploading(true);

    try {
      const uploaded: File[] = [];
      for (const file of Array.from(files)) {
        await dataService.uploadFile(file);
        uploaded.push(file);
      }
      setUploadedFiles(prev => [...prev, ...uploaded]);
      toast({
        title: 'Files uploaded successfully',
        description: `${uploaded.length} file(s) uploaded`,
      });

      // generate a default dashboard using the uploaded data
      await dashboardService.generateDashboard({
        title: 'My Dashboard',
        topics: ['Impact Overview', 'SDG Alignment']
      });
      navigate('/dashboard');
    } catch (error) {
      console.error(error);
      toast({
        title: 'Upload failed',
        description: 'Please try again',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleIntegration = (service: string) => {
    toast({
      title: `${service} Integration`,
      description: `${service} integration will be configured here`,
    });
  };

  const skipUpload = () => {
    navigate('/dashboard');
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Upload Data</h1>
        <Button variant="outline" onClick={skipUpload}>
          Skip for now
        </Button>
      </div>

      {/* File Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Files</CardTitle>
          <CardDescription>
            Upload your impact data files in any common format
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <UploadIcon className="mx-auto h-12 w-12 text-gray-400" />
            <div className="mt-4">
              <label htmlFor="file-upload" className="cursor-pointer">
                <span className="text-lg font-medium text-gray-900">
                  Click to upload files
                </span>
                <span className="text-gray-500"> or drag and drop</span>
              </label>
              <Input
                id="file-upload"
                type="file"
                multiple
                accept="*/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Files up to 10MB
            </p>
          </div>

          {uploadedFiles.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium text-gray-900 mb-2">Uploaded Files:</h4>
              <div className="space-y-2">
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center p-2 bg-gray-50 rounded">
                    <FileText className="h-4 w-4 text-gray-500 mr-2" />
                    <span className="text-sm">{file.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {isUploading && (
            <div className="mt-4 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-mega-primary mx-auto"></div>
              <p className="text-sm text-gray-600 mt-2">Processing files...</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Integration Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Database className="mr-2 h-5 w-5" />
              Xero
            </CardTitle>
            <CardDescription>
              Connect your Xero account for financial data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => handleIntegration('Xero')}
              className="w-full"
            >
              Connect Xero
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Sheet className="mr-2 h-5 w-5" />
              Google Sheets
            </CardTitle>
            <CardDescription>
              Sync data from your Google Sheets
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => handleIntegration('Google Sheets')}
              className="w-full"
            >
              Connect Google Sheets
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="mr-2 h-5 w-5" />
              Google Docs
            </CardTitle>
            <CardDescription>
              Import text data from Google Docs
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => handleIntegration('Google Docs')}
              className="w-full"
            >
              Connect Google Docs
            </Button>
          </CardContent>
        </Card>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="text-center">
          <Button onClick={() => navigate('/dashboard')} size="lg">
            Continue to Dashboard
          </Button>
        </div>
      )}
    </div>
  );
};

export default Upload;
