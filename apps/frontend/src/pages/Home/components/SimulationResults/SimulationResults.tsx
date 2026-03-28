import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Fade from '@mui/material/Fade';
import LinearProgress from '@mui/material/LinearProgress';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import useMediaQuery from '@mui/material/useMediaQuery';

import type { PredictResponse } from '~/api/types';

import type { AnimProbs } from '../../hooks/useMatchPrediction';
import { SIM_TOTAL } from '../../hooks/useMatchPrediction';
import { ModelProbBars } from '../ModelProbBars/ModelProbBars';
import { SimCounter } from '../SimCounter/SimCounter';
import { sx } from './styles';

interface Props {
  prediction: PredictResponse;
  home: string | null;
  away: string | null;
  isSimulating: boolean;
  isResult: boolean;
  simProgress: number;
  mlAnimProbs: AnimProbs;
  poissonAnimProbs: AnimProbs;
}

export function SimulationResults({
  prediction,
  home,
  away,
  isSimulating,
  isResult,
  simProgress,
  mlAnimProbs,
  poissonAnimProbs,
}: Readonly<Props>): JSX.Element {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const divider = isMobile ? (
    <Divider sx={sx.divider} />
  ) : (
    <Divider orientation="vertical" flexItem sx={sx.dividerVertical} />
  );

  return (
    <Fade in>
      <Paper sx={sx.card}>
        {isSimulating && (
          <Box sx={sx.progressContainer}>
            <LinearProgress variant="determinate" value={simProgress * 100} sx={sx.progressBar} />
            <SimCounter count={Math.round(simProgress * SIM_TOTAL)} total={SIM_TOTAL} />
          </Box>
        )}

        {isResult && (
          <Box sx={sx.predictionHeader}>
            <Typography variant="body2" sx={sx.predictionLabel}>
              Prediction
            </Typography>
            <Typography variant="h5" sx={sx.predictionTeams}>
              {home}{' '}
              <Box component="span" sx={sx.vsText}>
                vs
              </Box>{' '}
              {away}
            </Typography>
          </Box>
        )}

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={0} divider={divider}>
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
            variant="ml"
            compact={isMobile}
          />
          <ModelProbBars
            title="Poisson Baseline"
            subtitle={
              isResult
                ? `\u03BB home ${prediction.poisson.homeLambda.toFixed(2)}  \u00B7  \u03BB away ${prediction.poisson.awayLambda.toFixed(2)}`
                : null
            }
            homeWin={prediction.poisson.homeWin}
            draw={prediction.poisson.draw}
            awayWin={prediction.poisson.awayWin}
            home={home}
            away={away}
            animProbs={isSimulating ? poissonAnimProbs : null}
            isSimulating={isSimulating}
            variant="poisson"
            compact={isMobile}
          />
        </Stack>
      </Paper>
    </Fade>
  );
}
