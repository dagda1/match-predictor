import { useQuery } from '@tanstack/react-query';
import xior from 'xior';

import type { Team } from '~/api/types';

const api = xior.create({ baseURL: '/api' });

interface UseTeamsResult {
  teams: Team[];
  isLoading: boolean;
  error: Error | null;
}

export function useTeams(): UseTeamsResult {
  const { data, isLoading, error } = useQuery({
    queryKey: ['teams'],
    queryFn: async () => {
      const response = await api.get<Team[]>('/teams');
      return response.data;
    },
  });

  return {
    teams: data ?? [],
    isLoading,
    error,
  };
}
