import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import type { ModelVariant } from '../ModelProbBars/ModelProbBars';
import { getBarSx, getValueSx, sx } from './styles';

type Outcome = 'homeWin' | 'draw' | 'awayWin';

interface Props {
  label: string;
  value: number;
  animatedValue: number | null;
  outcome: Outcome;
  variant: ModelVariant;
  compact: boolean;
}

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function ProbBar({ label, value, animatedValue, outcome, variant, compact }: Readonly<Props>): JSX.Element {
  const display = animatedValue ?? value;

  return (
    <Box sx={compact ? sx.rootCompact : sx.root}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={sx.labelRow}>
        <Typography variant="body2" noWrap sx={compact ? sx.labelCompact : sx.label}>
          {label}
        </Typography>
        <Typography variant="body2" sx={getValueSx(compact, variant, outcome)}>
          {pct(display)}
        </Typography>
      </Stack>
      <Box sx={compact ? sx.trackCompact : sx.track}>
        <Box sx={getBarSx(display * 100, variant, outcome, animatedValue !== null)} />
      </Box>
    </Box>
  );
}
