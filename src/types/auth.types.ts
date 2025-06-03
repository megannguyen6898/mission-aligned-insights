
export interface User {
  id: number;
  email: string;
  name: string;
  organization_name: string;
  mission?: string;
  audience?: string;
  sector?: string;
  region?: string;
  organization_size?: string;
  key_goals?: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  organization_name: string;
  mission?: string;
  audience?: string;
  sector?: string;
  region?: string;
  organization_size?: string;
  key_goals?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}
