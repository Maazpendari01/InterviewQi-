// src/lib/api.ts (or wherever your api.ts is located)

// ✅ Correct port for your backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ========================================
// Types matching YOUR backend
// ========================================

export interface StartInterviewRequest {
  category: 'coding' | 'system_design' | 'behavioral';
  difficulty?: 'easy' | 'medium' | 'hard';
}

export interface StartInterviewResponse {
  session_id: string;
  question: string;
  question_number: number;
  category: string;
}

export interface SubmitAnswerRequest {
  session_id: string;
  answer: string;
}

export interface SubmitAnswerResponse {
  evaluation: string;
  score: number;
  question_number: number;
  continue: boolean;
  next_question?: string;
  next_question_id?: string;
  message?: string;
}

export interface SessionSummary {
  session_id: string;
  category: string;
  difficulty: string;
  started_at: string;
  completed_at?: string;
  total_questions: number;
  average_score: number;
  is_completed: boolean;
  responses: Array<{
    question_number: number;
    question: string;
    answer: string;
    score: number;
    evaluation: string;
  }>;
  transcript: any;
}

export interface HealthCheck {
  api: string;
  database: string;
  status: string;
}

// ========================================
// API Client Class
// ========================================

class InterviewAPI {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    console.log(`🚀 API Request: ${options.method || 'GET'} ${url}`);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`
        }));
        console.error('❌ API Error:', error);
        throw new Error(error.detail || error.message || `Request failed: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ API Response:', data);
      return data;
    } catch (error) {
      console.error('❌ Network Error:', error);
      throw error;
    }
  }

  // ========================================
  // Interview Endpoints (matching YOUR backend)
  // ========================================

  /**
   * Start a new interview session
   * POST /api/interview/start
   */
  async startInterview(data: StartInterviewRequest): Promise<StartInterviewResponse> {
    return this.request<StartInterviewResponse>('/api/interview/start', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Submit an answer to the current question
   * POST /api/interview/answer
   */
  async submitAnswer(data: SubmitAnswerRequest): Promise<SubmitAnswerResponse> {
    return this.request<SubmitAnswerResponse>('/api/interview/answer', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Get interview session summary
   * GET /api/interview/{session_id}/summary
   */
  async getSessionSummary(sessionId: string): Promise<SessionSummary> {
    return this.request<SessionSummary>(`/api/interview/${sessionId}/summary`);
  }

  /**
   * Get recent interview sessions
   * GET /api/interview/sessions/recent
   */
  async getRecentSessions(limit: number = 10): Promise<{
    total: number;
    sessions: Array<{
      session_id: string;
      category: string;
      started_at: string;
      completed: boolean;
      average_score: number;
      total_questions: number;
    }>;
  }> {
    return this.request(`/api/interview/sessions/recent?limit=${limit}`);
  }

  // ========================================
  // Analytics Endpoints
  // ========================================

  /**
   * Get platform statistics
   * GET /api/analytics/stats
   */
  async getPlatformStats(): Promise<{
    total_sessions: number;
    completed_sessions: number;
    completion_rate: number;
    average_score: number;
    by_category: Record<string, number>;
  }> {
    return this.request('/api/analytics/stats');
  }

  /**
   * Get weak areas analysis
   * GET /api/analytics/weak-areas
   */
  async getWeakAreas(threshold: number = 60, userId?: number): Promise<{
    threshold: number;
    weak_areas: any[];
    total_categories: number;
  }> {
    const params = new URLSearchParams({ threshold: threshold.toString() });
    if (userId) params.append('user_id', userId.toString());

    return this.request(`/api/analytics/weak-areas?${params}`);
  }

  /**
   * Get user progress
   * GET /api/analytics/progress/{user_id}
   */
  async getUserProgress(userId: number, limit: number = 20): Promise<any> {
    return this.request(`/api/analytics/progress/${userId}?limit=${limit}`);
  }

  /**
   * Get leaderboard
   * GET /api/analytics/leaderboard
   */
  async getLeaderboard(category?: string, limit: number = 10): Promise<{
    leaderboard: Array<{
      rank: number;
      session_id: string;
      category: string;
      score: number;
      questions: number;
      date: string;
    }>;
    total_entries: number;
  }> {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (category) params.append('category', category);

    return this.request(`/api/analytics/leaderboard?${params}`);
  }

  // ========================================
  // Health Check
  // ========================================

  /**
   * Check API and database health
   * GET /health
   */
  async healthCheck(): Promise<HealthCheck> {
    return this.request('/health');
  }
}

// ========================================
// Export singleton instance
// ========================================

export const api = new InterviewAPI(API_BASE_URL);

// ========================================
// Helper functions
// ========================================

export const handleAPIError = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred. Please try again.';
};

// Test connection helper
export const testConnection = async (): Promise<boolean> => {
  try {
    const health = await api.healthCheck();
    console.log('✅ Backend connection successful:', health);
    return health.status === 'healthy';
  } catch (error) {
    console.error('❌ Backend connection failed:', error);
    return false;
  }
};
