
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { dashboardService } from '../services/dashboard.service';

const dashboardTopics = [
  'Impact Overview',
  'SDG Alignment',
  'Financial Performance',
  'Beneficiary Demographics',
  'Program Outcomes',
  'Geographic Distribution',
  'Time Series Analysis',
  'Comparative Analysis'
];

const sampleData = {
  impact: [
    { name: 'Education', before: 45, after: 78, improvement: 33 },
    { name: 'Health', before: 52, after: 85, improvement: 33 },
    { name: 'Income', before: 38, after: 67, improvement: 29 },
    { name: 'Employment', before: 41, after: 73, improvement: 32 }
  ],
  sdg: [
    { sdg: 1, title: 'No Poverty', score: 85, color: '#E5243B' },
    { sdg: 3, title: 'Good Health', score: 78, color: '#4C9F38' },
    { sdg: 4, title: 'Quality Education', score: 92, color: '#C5192D' },
    { sdg: 8, title: 'Decent Work', score: 67, color: '#A21942' }
  ],
  timeline: [
    { month: 'Jan', beneficiaries: 120, impact: 65 },
    { month: 'Feb', beneficiaries: 145, impact: 72 },
    { month: 'Mar', beneficiaries: 178, impact: 78 },
    { month: 'Apr', beneficiaries: 203, impact: 85 },
    { month: 'May', beneficiaries: 234, impact: 89 },
    { month: 'Jun', beneficiaries: 267, impact: 92 }
  ]
};

const Dashboard: React.FC = () => {
  const [selectedTopic, setSelectedTopic] = useState('Impact Overview');
  const [dashboards, setDashboards] = useState<any[]>([]);

  useEffect(() => {
    const fetchDashboards = async () => {
      try {
        const loadedDashboards = await dashboardService.listDashboards();
        if (loadedDashboards && loadedDashboards.length > 0) {
          setDashboards(loadedDashboards);
        }
      } catch (e) {
        console.error('Failed to load dashboards', e);
      }
    };
    fetchDashboards();
  }, []);

  const renderContent = (dashboardData: any) => {
    switch (selectedTopic) {
      case 'Impact Overview':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Before vs After Impact</CardTitle>
                <CardDescription>Improvements across key metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={dashboardData.impact || sampleData.impact}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="before" fill="#f3f4f6" />
                    <Bar dataKey="after" fill="#20c6cd" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Impact Journey</CardTitle>
                <CardDescription>Growth over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={dashboardData.timeline || sampleData.timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="beneficiaries" stroke="#20c6cd" strokeWidth={3} />
                    <Line type="monotone" dataKey="impact" stroke="#000000" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        );
        
      case 'SDG Alignment':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>SDG Impact Meter</CardTitle>
                <CardDescription>Your alignment with Sustainable Development Goals</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {(dashboardData.sdg || sampleData.sdg).map((sdg: any) => (
                    <div key={sdg.sdg} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">SDG {sdg.sdg}: {sdg.title}</span>
                        <span className="text-sm text-gray-600">{sdg.score}%</span>
                      </div>
                      <Progress value={sdg.score} className="h-3" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        );
        
      default:
        return (
          <Card>
            <CardHeader>
              <CardTitle>{selectedTopic}</CardTitle>
              <CardDescription>Dashboard content for {selectedTopic}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Dashboard content for {selectedTopic} will be displayed here based on your uploaded data.
              </p>
            </CardContent>
          </Card>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <Select value={selectedTopic} onValueChange={setSelectedTopic}>
          <SelectTrigger className="w-[250px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {dashboardTopics.map((topic) => (
              <SelectItem key={topic} value={topic}>
                {topic}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      
      {dashboards.length > 0
        ? dashboards.map((dashboard) => (
            <div key={dashboard.id} className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-800">{dashboard.title}</h2>
              {renderContent(dashboard.chart_data || sampleData)}
            </div>
          ))
        : renderContent(sampleData)}
    </div>
  );
};

export default Dashboard;
