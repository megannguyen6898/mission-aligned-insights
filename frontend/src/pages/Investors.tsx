
import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Filter, MapPin, DollarSign, Target, ExternalLink, MessageSquare } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const sampleInvestors = [
  {
    id: 1,
    name: 'Impact Ventures Fund',
    focus_areas: ['Education', 'Healthcare'],
    funding_type: 'Grant',
    region: 'North America',
    sdg_tags: [3, 4, 8],
    ticket_size_min: 50000,
    ticket_size_max: 500000,
    website_url: 'https://impactventures.com',
    match_score: 92,
    description: 'Leading impact investor focused on scalable solutions in education and healthcare'
  },
  {
    id: 2,
    name: 'Green Future Capital',
    focus_areas: ['Environment', 'Climate'],
    funding_type: 'Equity',
    region: 'Europe',
    sdg_tags: [6, 7, 13],
    ticket_size_min: 100000,
    ticket_size_max: 2000000,
    website_url: 'https://greenfuture.eu',
    match_score: 87,
    description: 'Venture capital firm investing in climate solutions and environmental technology'
  },
  {
    id: 3,
    name: 'Social Impact Foundation',
    focus_areas: ['Poverty', 'Social Enterprise'],
    funding_type: 'Grant',
    region: 'Global',
    sdg_tags: [1, 2, 10],
    ticket_size_min: 25000,
    ticket_size_max: 300000,
    website_url: 'https://socialimpact.org',
    match_score: 84,
    description: 'Foundation supporting innovative approaches to poverty alleviation worldwide'
  }
];

const Investors: React.FC = () => {
  const [filteredInvestors, setFilteredInvestors] = useState(sampleInvestors);
  const [filters, setFilters] = useState({
    region: 'all',
    funding_type: 'all',
    min_amount: '',
    max_amount: ''
  });
  const [selectedInvestor, setSelectedInvestor] = useState<typeof sampleInvestors[0] | null>(null);
  const [pitchText, setPitchText] = useState('');
  const [isGeneratingPitch, setIsGeneratingPitch] = useState(false);
  const { toast } = useToast();

  const applyFilters = () => {
    let filtered = sampleInvestors;

    if (filters.region && filters.region !== 'all') {
      filtered = filtered.filter(inv => inv.region === filters.region || inv.region === 'Global');
    }

    if (filters.funding_type && filters.funding_type !== 'all') {
      filtered = filtered.filter(inv => inv.funding_type === filters.funding_type);
    }

    if (filters.min_amount) {
      const minAmount = parseInt(filters.min_amount);
      filtered = filtered.filter(inv => inv.ticket_size_max >= minAmount);
    }

    if (filters.max_amount) {
      const maxAmount = parseInt(filters.max_amount);
      filtered = filtered.filter(inv => inv.ticket_size_min <= maxAmount);
    }

    setFilteredInvestors(filtered);
  };

  const generatePitch = async (investor: typeof sampleInvestors[0]) => {
    setIsGeneratingPitch(true);
    setSelectedInvestor(investor);
    
    // Simulate AI pitch generation
    setTimeout(() => {
      const samplePitch = `Dear ${investor.name} team,

I hope this message finds you well. I'm reaching out from [Your Organization Name] because our mission aligns perfectly with your investment focus in ${investor.focus_areas.join(' and ')}.

Our organization has demonstrated significant impact in areas that match your SDG priorities (SDGs ${investor.sdg_tags.join(', ')}). We're seeking ${investor.funding_type.toLowerCase()} funding in the range of $${investor.ticket_size_min.toLocaleString()} - $${investor.ticket_size_max.toLocaleString()} to scale our proven impact model.

Key highlights:
• Direct alignment with your investment thesis
• Proven track record of measurable outcomes
• Scalable solution ready for growth
• Strong team with domain expertise

I would welcome the opportunity to discuss how our work could fit within your portfolio and create meaningful impact together.

Best regards,
[Your Name]`;

      setPitchText(samplePitch);
      setIsGeneratingPitch(false);
      toast({
        title: 'Pitch generated',
        description: 'AI has generated a personalized pitch for this investor',
      });
    }, 2000);
  };

  const requestIntroduction = (investor: typeof sampleInvestors[0]) => {
    toast({
      title: 'Introduction requested',
      description: `Introduction request sent to ${investor.name}`,
    });
  };

  const exportInvestors = () => {
    toast({
      title: 'Export started',
      description: 'Investor list is being exported to CSV',
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Investor Matching</h1>
        <Button onClick={exportInvestors} variant="outline">
          Export List
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="mr-2 h-5 w-5" />
            Filter Investors
          </CardTitle>
          <CardDescription>
            Narrow down your investor matches based on your preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Select value={filters.region} onValueChange={(value) => setFilters({...filters, region: value})}>
              <SelectTrigger>
                <SelectValue placeholder="Region" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Regions</SelectItem>
                <SelectItem value="North America">North America</SelectItem>
                <SelectItem value="Europe">Europe</SelectItem>
                <SelectItem value="Asia Pacific">Asia Pacific</SelectItem>
                <SelectItem value="Global">Global</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filters.funding_type} onValueChange={(value) => setFilters({...filters, funding_type: value})}>
              <SelectTrigger>
                <SelectValue placeholder="Funding Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="Grant">Grant</SelectItem>
                <SelectItem value="Equity">Equity</SelectItem>
                <SelectItem value="Debt">Debt</SelectItem>
              </SelectContent>
            </Select>

            <Input
              placeholder="Min Amount"
              value={filters.min_amount}
              onChange={(e) => setFilters({...filters, min_amount: e.target.value})}
            />

            <Input
              placeholder="Max Amount"
              value={filters.max_amount}
              onChange={(e) => setFilters({...filters, max_amount: e.target.value})}
            />
          </div>
          
          <Button onClick={applyFilters} className="mt-4">
            Apply Filters
          </Button>
        </CardContent>
      </Card>

      {/* Investor List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredInvestors.map((investor) => (
          <Card key={investor.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">{investor.name}</CardTitle>
                  <CardDescription className="mt-1">
                    {investor.description}
                  </CardDescription>
                </div>
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  {investor.match_score}% match
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center text-sm text-gray-600">
                  <MapPin className="mr-2 h-4 w-4" />
                  {investor.region}
                </div>
                
                <div className="flex items-center text-sm text-gray-600">
                  <DollarSign className="mr-2 h-4 w-4" />
                  ${investor.ticket_size_min.toLocaleString()} - ${investor.ticket_size_max.toLocaleString()} ({investor.funding_type})
                </div>
                
                <div className="flex items-center text-sm text-gray-600">
                  <Target className="mr-2 h-4 w-4" />
                  {investor.focus_areas.join(', ')}
                </div>
                
                <div className="flex flex-wrap gap-1 mt-2">
                  {investor.sdg_tags.map((sdg) => (
                    <Badge key={sdg} variant="outline" className="text-xs">
                      SDG {sdg}
                    </Badge>
                  ))}
                </div>
                
                <div className="flex space-x-2 mt-4">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button size="sm" onClick={() => generatePitch(investor)}>
                        Generate Pitch
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>Generated Pitch for {investor.name}</DialogTitle>
                        <DialogDescription>
                          AI-generated personalized pitch based on investor preferences
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        {isGeneratingPitch ? (
                          <div className="flex items-center justify-center p-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-mega-primary"></div>
                            <span className="ml-3">Generating personalized pitch...</span>
                          </div>
                        ) : (
                          <Textarea
                            value={pitchText}
                            onChange={(e) => setPitchText(e.target.value)}
                            rows={12}
                            className="font-mono text-sm"
                          />
                        )}
                        <div className="flex space-x-2">
                          <Button onClick={() => requestIntroduction(investor)}>
                            <MessageSquare className="mr-2 h-4 w-4" />
                            Request Introduction
                          </Button>
                          <Button variant="outline" asChild>
                            <a href={investor.website_url} target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="mr-2 h-4 w-4" />
                              Visit Website
                            </a>
                          </Button>
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>
                  
                  <Button variant="outline" size="sm" onClick={() => requestIntroduction(investor)}>
                    Request Intro
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Investors;
