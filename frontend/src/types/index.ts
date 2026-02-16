export interface User {
  id: number;
  email: string;
  username: string;
  role: 'superadmin' | 'admin' | 'operator';
  institution_id?: number;
  institution_name?: string;
  full_name: string;
  is_active: number;
}

export interface Session {
  id: number;
  institution_id: number;
  operator_id?: number;
  started_at: string;
  ended_at?: string;
  turns_count: number;
  is_active: boolean;
}

export interface LSPPrediction {
  label: string;
  confidence: number;
  is_confident: boolean;
  threshold: number;
  alternatives?: Array<{label: string; confidence: number}>;
}
