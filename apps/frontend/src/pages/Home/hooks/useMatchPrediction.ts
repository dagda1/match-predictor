import { useEffect, useState } from 'react';

import { usePrediction } from '~/hooks/usePrediction';
import { useTeams } from '~/hooks/useTeams';

import { useSimulationAnimation } from './useSimulationAnimation';

export type { AnimProbs } from './useSimulationAnimation';
export { SIM_TOTAL } from './useSimulationAnimation';

export type Phase = 'empty' | 'ready' | 'simulating' | 'result';

interface UseMatchPredictionResult {
  teams: string[];
  home: string | null;
  away: string | null;
  phase: Phase;
  prediction: ReturnType<typeof usePrediction>['data'];
  simProgress: number;
  mlAnimProbs: ReturnType<typeof useSimulationAnimation>['mlAnimProbs'];
  poissonAnimProbs: ReturnType<typeof useSimulationAnimation>['poissonAnimProbs'];
  revealedRows: number;
  setHome: (team: string | null) => void;
  setAway: (team: string | null) => void;
  handlePredict: () => void;
  handleReset: () => void;
}

export function useMatchPrediction(): UseMatchPredictionResult {
  const { teams: teamData } = useTeams();
  const { predict, data: prediction } = usePrediction();
  const animation = useSimulationAnimation();

  const [home, setHome] = useState<string | null>(null);
  const [away, setAway] = useState<string | null>(null);
  const [phase, setPhase] = useState<Phase>('empty');

  const teams = teamData.map((team) => team.name);

  useEffect(() => {
    if (home && away && phase === 'empty') {
      setPhase('ready');
    }
    if ((!home || !away) && phase === 'ready') {
      setPhase('empty');
    }
  }, [home, away, phase]);

  useEffect(() => {
    if (prediction && phase === 'simulating') {
      animation.startAnimation(prediction);
    }
  }, [prediction, phase]);

  useEffect(() => {
    if (!animation.isAnimating && phase === 'simulating' && prediction) {
      setPhase('result');
    }
  }, [animation.isAnimating, phase, prediction]);

  function handlePredict(): void {
    if (!home || !away) {
      return;
    }

    animation.resetAnimation();
    setPhase('simulating');
    predict({ homeTeamId: home, awayTeamId: away });
  }

  function handleReset(): void {
    setPhase(home && away ? 'ready' : 'empty');
    animation.resetAnimation();
  }

  return {
    teams,
    home,
    away,
    phase,
    prediction,
    simProgress: animation.simProgress,
    mlAnimProbs: animation.mlAnimProbs,
    poissonAnimProbs: animation.poissonAnimProbs,
    revealedRows: animation.revealedRows,
    setHome,
    setAway,
    handlePredict,
    handleReset,
  };
}
