import { useCallback, useEffect, useRef, useState } from 'react';

import type { PredictResponse } from '~/api/types';

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

interface UseSimulationAnimationResult {
  simProgress: number;
  mlAnimProbs: AnimProbs;
  poissonAnimProbs: AnimProbs;
  revealedRows: number;
  isAnimating: boolean;
  startAnimation: (response: PredictResponse) => void;
  resetAnimation: () => void;
}

export function useSimulationAnimation(): UseSimulationAnimationResult {
  const [simProgress, setSimProgress] = useState(0);
  const [mlAnimProbs, setMlAnimProbs] = useState<AnimProbs>(INITIAL_PROBS);
  const [poissonAnimProbs, setPoissonAnimProbs] = useState<AnimProbs>(INITIAL_PROBS);
  const [revealedRows, setRevealedRows] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const rafRef = useRef(0);

  const startAnimation = useCallback((response: PredictResponse) => {
    const start = performance.now();
    const { ml, poisson } = response;
    setIsAnimating(true);

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
        setIsAnimating(false);
      }
    };

    rafRef.current = requestAnimationFrame(tick);
  }, []);

  const resetAnimation = useCallback(() => {
    setSimProgress(0);
    setRevealedRows(0);
    setMlAnimProbs(INITIAL_PROBS);
    setPoissonAnimProbs(INITIAL_PROBS);
    setIsAnimating(false);
  }, []);

  useEffect(() => () => cancelAnimationFrame(rafRef.current), []);

  return {
    simProgress,
    mlAnimProbs,
    poissonAnimProbs,
    revealedRows,
    isAnimating,
    startAnimation,
    resetAnimation,
  };
}
