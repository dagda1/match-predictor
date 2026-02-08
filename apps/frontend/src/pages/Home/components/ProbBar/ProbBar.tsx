import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { sx, valueSx, barSx } from './styles';

interface ProbBarProps {
  label: string;
  value: number;
  color: string;
  animatedValue: number | null;
  compact: boolean;
}

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

export function ProbBar({ label, value, color, animatedValue, compact }: ProbBarProps): JSX.Element {
  const display = animatedValue ?? value;

  return (
    <Box sx={compact ? sx.rootCompact : sx.root}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={sx.labelRow}>
        <Typography variant="body2" noWrap sx={compact ? sx.labelCompact : sx.label}>
          {label}
        </Typography>
        <Typography variant="body2" sx={valueSx(compact, color)}>
          {pct(display)}
        </Typography>
      </Stack>
      <Box sx={compact ? sx.trackCompact : sx.track}>
        <Box sx={barSx(display * 100, color, animatedValue != null)} />
      </Box>
    </Box>
  );
}
