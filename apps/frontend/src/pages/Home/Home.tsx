import { useCallback, useEffect, useRef, useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';
import Fade from '@mui/material/Fade';
import LinearProgress from '@mui/material/LinearProgress';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Typography from '@mui/material/Typography';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';
import type { PredictResponse } from '~/api/types';
import { fetchPrediction, fetchTeams } from '~/api/predict';
import { ModelProbBars } from './components/ModelProbBars/ModelProbBars';
import { ScorelineTable } from './components/ScorelineTable/ScorelineTable';
import { SimCounter } from './components/SimCounter/SimCounter';
import { TeamPicker } from './components/TeamPicker/TeamPicker';
import { sx, getModelColors, tabsIndicatorSx } from './styles';

type Phase = 'empty' | 'ready' | 'simulating' | 'result';

interface AnimProbs {
  h: number;
  d: number;
  a: number;
}

const INITIAL_PROBS: AnimProbs = { h: 0.333, d: 0.333, a: 0.333 };
const SIM_DURATION = 2600;
const SIM_TOTAL = 10_000;

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

export function Home(): JSX.Element {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const colors = getModelColors(theme.palette.mode);

  const [teams, setTeams] = useState<string[]>([]);
  const [home, setHome] = useState<string | null>(null);
  const [away, setAway] = useState<string | null>(null);
  const [phase, setPhase] = useState<Phase>('empty');
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [simProgress, setSimProgress] = useState(0);
  const [mlAnimProbs, setMlAnimProbs] = useState<AnimProbs>(INITIAL_PROBS);
  const [poissonAnimProbs, setPoissonAnimProbs] = useState<AnimProbs>(INITIAL_PROBS);
  const [revealedRows, setRevealedRows] = useState(0);
  const [scoreTab, setScoreTab] = useState(0);
  const rafRef = useRef(0);

  useEffect(() => {
    fetchTeams()
      .then((result) => setTeams(result.map((t) => t.name)))
      .catch((error) => {
        console.error('failed to fetch teams', error);
      });
  }, []);

  useEffect(() => {
    if (home && away && phase === 'empty') setPhase('ready');
    if ((!home || !away) && phase === 'ready') setPhase('empty');
  }, [home, away, phase]);

  const animateResults = useCallback((response: PredictResponse) => {
    const start = performance.now();
    const { ml, poisson } = response;

    const tick = (now: number): void => {
      const elapsed = now - start;
      const t = Math.min(elapsed / SIM_DURATION, 1);
      const ease = 1 - Math.pow(1 - t, 3);
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

      if (t < 1) {
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
    if (!home || !away) return;

    setSimProgress(0);
    setRevealedRows(0);
    setScoreTab(0);
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

  const isSimulating = phase === 'simulating';
  const showResult = (isSimulating || phase === 'result') && prediction !== null;

  const divider = isMobile
    ? <Divider sx={sx.divider} />
    : <Divider orientation="vertical" flexItem sx={sx.dividerVertical} />;

  return (
    <Container maxWidth="md" sx={sx.container}>
      <Stack spacing={{ xs: 2, sm: 3 }}>
        <Paper sx={sx.card}>
          <Typography variant="h5" sx={sx.title}>
            Match Predictor
          </Typography>
          <Typography variant="subtitle2" sx={sx.subtitle}>
            ML model + Poisson baseline
          </Typography>

          <Stack direction="column" spacing={1.5} sx={sx.teamStack}>
            <TeamPicker label="Home team" value={home} onChange={setHome} options={teams} exclude={away} />
            <TeamPicker label="Away team" value={away} onChange={setAway} options={teams} exclude={home} />
          </Stack>

          {phase !== 'result' && (
            <Button
              variant="contained"
              fullWidth
              disabled={phase === 'empty' || isSimulating}
              onClick={handlePredict}
              disableElevation
              sx={phase === 'empty' || isSimulating ? sx.predictButtonDisabled : sx.predictButton}
            >
              {isSimulating ? 'Simulating\u2026' : 'Predict'}
            </Button>
          )}

          {phase === 'result' && (
            <Button variant="outlined" fullWidth onClick={handleReset} sx={sx.newPredButton}>
              New prediction
            </Button>
          )}
        </Paper>

        {showResult && prediction && (
          <Fade in>
            <Paper sx={sx.card}>
              {isSimulating && (
                <Box sx={sx.progressContainer}>
                  <LinearProgress
                    variant="determinate"
                    value={simProgress * 100}
                    sx={sx.progressBar}
                  />
                  <SimCounter count={Math.round(simProgress * SIM_TOTAL)} total={SIM_TOTAL} />
                </Box>
              )}

              {phase === 'result' && (
                <Box sx={sx.predictionHeader}>
                  <Typography variant="body2" sx={sx.predictionLabel}>
                    Prediction
                  </Typography>
                  <Typography variant="h5" sx={sx.predictionTeams}>
                    {home} <Box component="span" sx={sx.vsText}>vs</Box> {away}
                  </Typography>
                </Box>
              )}

              <Stack
                direction={{ xs: 'column', sm: 'row' }}
                spacing={0}
                divider={divider}
              >
                <ModelProbBars
                  title="ML Model"
                  subtitle={null}
                  homeWin={prediction.ml.homeWin}
                  draw={prediction.ml.draw}
                  awayWin={prediction.ml.awayWin}
                  home={home}
                  away={away}
                  animProbs={isSimulating ? mlAnimProbs : null}
                  isSimulating={isSimulating}
                  colors={colors.ml}
                  compact={isMobile}
                />
                <ModelProbBars
                  title="Poisson Baseline"
                  subtitle={phase === 'result' ? `\u03BB home ${prediction.poisson.homeLambda.toFixed(2)}  \u00B7  \u03BB away ${prediction.poisson.awayLambda.toFixed(2)}` : null}
                  homeWin={prediction.poisson.homeWin}
                  draw={prediction.poisson.draw}
                  awayWin={prediction.poisson.awayWin}
                  home={home}
                  away={away}
                  animProbs={isSimulating ? poissonAnimProbs : null}
                  isSimulating={isSimulating}
                  colors={colors.poisson}
                  compact={isMobile}
                />
              </Stack>
            </Paper>
          </Fade>
        )}

        {showResult && prediction && (
          <Fade in timeout={400}>
            <Paper sx={sx.card}>
              <Typography variant="subtitle2" sx={sx.scoreSubtitle}>
                Most likely scorelines
              </Typography>

              <Tabs
                value={scoreTab}
                onChange={(_, v: number) => setScoreTab(v)}
                variant={isMobile ? 'fullWidth' : 'standard'}
                sx={tabsIndicatorSx(scoreTab)}
              >
                <Tab label="ML Model" sx={sx.mlTab} />
                <Tab label="Poisson" sx={sx.poissonTab} />
              </Tabs>

              {scoreTab === 0 && (
                <ScorelineTable
                  scorelines={prediction.ml.scorelines}
                  revealed={isSimulating ? revealedRows : null}
                  chipColor={colors.ml.chip}
                  chipAccentBg={colors.ml.chipAccentBg}
                  chipAccentText={colors.ml.chipAccentText}
                />
              )}
              {scoreTab === 1 && (
                <ScorelineTable
                  scorelines={prediction.poisson.scorelines}
                  revealed={isSimulating ? revealedRows : null}
                  chipColor={colors.poisson.chip}
                  chipAccentBg={colors.poisson.chipAccentBg}
                  chipAccentText={colors.poisson.chipAccentText}
                />
              )}
            </Paper>
          </Fade>
        )}
      </Stack>
    </Container>
  );
}

export default Home;
