import { useCallback, useEffect, useRef, useState } from 'react';

import { fetchPrediction, fetchTeams } from '~/api/predict';
import type { PredictResponse } from '~/api/types';

export type Phase = 'empty' | 'ready' | 'simulating' | 'result';

export interface AnimProbs {
  h: number;
  d: number;
  a: number;
}

const INITIAL_PROBS: AnimProbs = { h: 0.333, d: 0.333, a: 0.333 };
const SIM_DURATION = 2600;
export const SIM_TOTAL = 10_000;

function lerp(start: number, end: number, progress: number): number {
  return start + (end - start) * progress;
}

interface UseMatchPredictionResult {
  teams: string[];
  home: string | null;
  away: string | null;
  phase: Phase;
  prediction: PredictResponse | null;
  simProgress: number;
  mlAnimProbs: AnimProbs;
  poissonAnimProbs: AnimProbs;
  revealedRows: number;
  setHome: (team: string | null) => void;
  setAway: (team: string | null) => void;
  handlePredict: () => void;
  handleReset: () => void;
}

export function useMatchPrediction(): UseMatchPredictionResult {
  const [teams, setTeams] = useState<string[]>([]);
  const [home, setHome] = useState<string | null>(null);
  const [away, setAway] = useState<string | null>(null);
  const [phase, setPhase] = useState<Phase>('empty');
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [simProgress, setSimProgress] = useState(0);
  const [mlAnimProbs, setMlAnimProbs] = useState<AnimProbs>(INITIAL_PROBS);
  const [poissonAnimProbs, setPoissonAnimProbs] = useState<AnimProbs>(INITIAL_PROBS);
  const [revealedRows, setRevealedRows] = useState(0);
  const rafRef = useRef(0);

  useEffect(() => {
    fetchTeams()
      .then((result) => setTeams(result.map((team) => team.name)))
      .catch((error) => {
        console.error('failed to fetch teams', error);
      });
  }, []);

  useEffect(() => {
    if (home && away && phase === 'empty') {
      setPhase('ready');
    }
    if ((!home || !away) && phase === 'ready') {
      setPhase('empty');
    }
  }, [home, away, phase]);

  const animateResults = useCallback((response: PredictResponse) => {
    const start = performance.now();
    const { ml, poisson } = response;

    const tick = (now: number): void => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / SIM_DURATION, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      const jitter = (1 - ease) * (Math.random() - 0.5) * 0.08;

      setSimProgress(ease);
      setMlAnimProbs({
        h: lerp(0.333, ml.homeWin, ease) + jitter,
        d: lerp(0.333, ml.draw, ease) - jitter * 0.5,
        a: lerp(0.333, ml.awayWin, ease) - jitter * 0.5,
      });
      setPoissonAnimProbs({
        h: lerp(0.333, poisson.homeWin, ease) + jitter * 0.7,
        d: lerp(0.333, poisson.draw, ease) - jitter * 0.3,
        a: lerp(0.333, poisson.awayWin, ease) - jitter * 0.4,
      });
      setRevealedRows(Math.min(10, Math.floor(ease * 13)));

      if (progress < 1) {
        rafRef.current = requestAnimationFrame(tick);
      } else {
        setMlAnimProbs({ h: ml.homeWin, d: ml.draw, a: ml.awayWin });
        setPoissonAnimProbs({ h: poisson.homeWin, d: poisson.draw, a: poisson.awayWin });
        setRevealedRows(10);
        setTimeout(() => setPhase('result'), 200);
      }
    };

    rafRef.current = requestAnimationFrame(tick);
  }, []);

  useEffect(() => () => cancelAnimationFrame(rafRef.current), []);

  function handlePredict(): void {
    if (!home || !away) {
      return;
    }

    setSimProgress(0);
    setRevealedRows(0);
    setMlAnimProbs(INITIAL_PROBS);
    setPoissonAnimProbs(INITIAL_PROBS);

    fetchPrediction(home, away)
      .then((response) => {
        setPrediction(response);
        setPhase('simulating');
        animateResults(response);
      })
      .catch((error) => {
        console.error('prediction failed', { home, away }, error);
      });
  }

  function handleReset(): void {
    setPhase(home && away ? 'ready' : 'empty');
    setSimProgress(0);
    setRevealedRows(0);
  }

  return {
    teams,
    home,
    away,
    phase,
    prediction,
    simProgress,
    mlAnimProbs,
    poissonAnimProbs,
    revealedRows,
    setHome,
    setAway,
    handlePredict,
    handleReset,
  };
}
