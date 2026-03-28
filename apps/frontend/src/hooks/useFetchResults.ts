import type { UseSuspenseQueryResult } from '@tanstack/react-query';
import { useSuspenseQuery } from '@tanstack/react-query';
import xior from 'xior';

import type { ResultsResponse } from '~/api/types';

const api = xior.create({ baseURL: '/api' });

interface UseFetchResultsProps {
  startDate: string;
  endDate?: string;
}

export function useFetchResults({ startDate, endDate }: UseFetchResultsProps): UseSuspenseQueryResult<ResultsResponse> {
  return useSuspenseQuery<ResultsResponse>({
    queryKey: ['results', startDate, endDate],
    queryFn: async () => {
      const params = new URLSearchParams({ startDate });
      if (endDate) {
        params.set('endDate', endDate);
      }
      const response = await api.get<ResultsResponse>(`/results?${params}`);
      return response.data;
    },
  });
}
