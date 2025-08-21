
export interface DashboardTopic {
  id: string;
  name: string;
  description: string;
}

export interface ChartData {
  name: string;
  value: number;
  before?: number;
  after?: number;
  category?: string;
}

export interface DashboardConfig {
  topics: string[];
  filters: Record<string, any>;
  dateRange?: {
    start: string;
    end: string;
  };
}

export interface SDGAlignment {
  sdg: number;
  title: string;
  score: number;
  description: string;
}
