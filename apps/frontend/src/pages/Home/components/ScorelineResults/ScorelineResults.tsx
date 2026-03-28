import Fade from '@mui/material/Fade';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import type { PredictResponse } from '~/api/types';

import { ScorelineTable } from '../ScorelineTable/ScorelineTable';
import { sx } from './styles';

interface Props {
  prediction: PredictResponse;
  isSimulating: boolean;
  revealedRows: number;
}

export function ScorelineResults({ prediction, isSimulating, revealedRows }: Readonly<Props>): JSX.Element {
  return (
    <Fade in timeout={400}>
      <div>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={{ xs: 2, sm: 2.5 }}>
          <Paper sx={sx.scoreCard}>
            <Typography variant="subtitle2" sx={sx.scoreSubtitle}>
              ML Model scorelines
            </Typography>
            <ScorelineTable
              scorelines={prediction.ml.scorelines}
              revealed={isSimulating ? revealedRows : null}
              variant="ml"
            />
          </Paper>
          <Paper sx={sx.scoreCard}>
            <Typography variant="subtitle2" sx={sx.scoreSubtitle}>
              Poisson scorelines
            </Typography>
            <ScorelineTable
              scorelines={prediction.poisson.scorelines}
              revealed={isSimulating ? revealedRows : null}
              variant="poisson"
            />
          </Paper>
        </Stack>
      </div>
    </Fade>
  );
}
