export interface SignupRequest {
  email: string;
  password: string;
  name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  email: string;
  name: string | null;
}

export interface UserResponse {
  id: number;
  email: string | null;
  name: string | null;
  created_at: string;
}
