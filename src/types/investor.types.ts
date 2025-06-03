
export interface Investor {
  id: number;
  name: string;
  focus_areas: string[];
  funding_type: string;
  region: string;
  sdg_tags: number[];
  ticket_size_min: number;
  ticket_size_max: number;
  website_url?: string;
  contact_email?: string;
  description?: string;
}

export interface InvestorMatch {
  investor: Investor;
  match_score: number;
  reasons: string[];
}

export interface PitchSummary {
  id: number;
  investor_id: number;
  pitch_text: string;
  generated_at: string;
}

export interface InvestorFilters {
  region?: string;
  funding_type?: string;
  min_amount?: number;
  max_amount?: number;
  sdg_focus?: number[];
}
