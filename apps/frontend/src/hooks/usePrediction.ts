import { useMutation } from '@tanstack/react-query';
import xior from 'xior';

import type { PredictResponse } from '~/api/types';

const api = xior.create({ baseURL: '/api' });

interface PredictionParams {
  homeTeamId: string;
  awayTeamId: string;
}

interface UsePredictionResult {
  predict: (params: PredictionParams) => void;
  data: PredictResponse | undefined;
  isPending: boolean;
  error: Error | null;
}

export function usePrediction(): UsePredictionResult {
  const { mutate, data, isPending, error } = useMutation({
    mutationFn: async (params: PredictionParams) => {
      const response = await api.post<PredictResponse>('/predict', params);
      return response.data;
    },
  });

  return {
    predict: mutate,
    data,
    isPending,
    error,
  };
}
