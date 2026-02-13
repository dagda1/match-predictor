import type { UseSuspenseQueryResult } from '@tanstack/react-query';
import { useSuspenseQuery } from '@tanstack/react-query';

import { fetchResults } from '~/api/predict';
import type { ResultsResponse } from '~/api/types';

interface UseFetchResultsProps {
  startDate: string;
  endDate?: string;
}

export function useFetchResults({ startDate, endDate }: UseFetchResultsProps): UseSuspenseQueryResult<ResultsResponse> {
  return useSuspenseQuery<ResultsResponse>({
    queryKey: ['results', startDate, endDate],
    queryFn: () => fetchResults(startDate, endDate),
  });
}
