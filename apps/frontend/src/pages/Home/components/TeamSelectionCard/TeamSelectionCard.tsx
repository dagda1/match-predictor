import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import type { Phase } from '../../hooks/useMatchPrediction';
import { TeamPicker } from '../TeamPicker/TeamPicker';
import { sx } from './styles';

interface Props {
  home: string | null;
  away: string | null;
  teams: string[];
  teamsLoading: boolean;
  phase: Phase;
  onHomeChange: (team: string | null) => void;
  onAwayChange: (team: string | null) => void;
  onPredict: () => void;
  onReset: () => void;
}

export function TeamSelectionCard({
  home,
  away,
  teams,
  teamsLoading,
  phase,
  onHomeChange,
  onAwayChange,
  onPredict,
  onReset,
}: Readonly<Props>): JSX.Element {
  const isSimulating = phase === 'simulating';
  const isResult = phase === 'result';

  return (
    <Paper sx={sx.card}>
      <Typography variant="h5" component="h1" sx={sx.title}>
        Match Predictor
      </Typography>
      <Typography variant="subtitle2" sx={sx.subtitle}>
        ML model + Poisson baseline
      </Typography>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} sx={sx.teamStack}>
        <TeamPicker label="Home team" value={home} onChange={onHomeChange} options={teams} exclude={away} loading={teamsLoading} />
        <TeamPicker label="Away team" value={away} onChange={onAwayChange} options={teams} exclude={home} loading={teamsLoading} />
      </Stack>

      <Button
        variant={isResult ? 'outlined' : 'contained'}
        fullWidth
        disabled={phase === 'empty' || isSimulating}
        onClick={isResult ? onReset : onPredict}
        disableElevation
        sx={isResult ? sx.actionButton : sx.predictButton}
        color="primary"
      >
        {isSimulating ? 'Simulating\u2026' : isResult ? 'New prediction' : 'Predict'}
      </Button>
    </Paper>
  );
}
