import { useState, useEffect } from 'react';

interface UserProgress {
  essays_written: number;
  average_score: number;
  best_score: number;
  improvement_rate: number;
  task_achievement_avg: number;
  coherence_cohesion_avg: number;
  lexical_resource_avg: number;
  grammatical_range_avg: number;
  l1_errors_total: number;
  interlanguage_errors_total: number;
  discourse_errors_total: number;
}

interface UserStats {
  total_points: number;
  level: number;
  streak_days: number;
  current_level: string;
}

interface UserProfile {
  user: {
    id: number;
    email: string;
    username: string;
    full_name: string;
    first_language: string;
    target_band_score: number;
    current_level: string;
    learning_goals: string;
    total_points: number;
    level: number;
    streak_days: number;
  };
  progress: UserProgress;
  recent_essays: any[];
  stats: UserStats;
}

export function useUserData() {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/user/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/auth/login';
          return;
        }
        throw new Error(`Failed to fetch user profile: ${response.statusText}`);
      }

      const data = await response.json();
      setUserProfile(data);
    } catch (err: any) {
      console.error('Error fetching user profile:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserProgress = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/user/progress`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch user progress: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err: any) {
      console.error('Error fetching user progress:', err);
      throw err;
    }
  };

  useEffect(() => {
    fetchUserProfile();
  }, []);

  return {
    userProfile,
    loading,
    error,
    refetch: fetchUserProfile,
    fetchUserProgress,
  };
}
