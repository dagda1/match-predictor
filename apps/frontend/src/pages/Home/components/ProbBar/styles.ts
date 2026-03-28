import type { SxProps, Theme } from '@mui/material/styles';

import type { ModelVariant } from '../ModelProbBars/ModelProbBars';

type Outcome = 'homeWin' | 'draw' | 'awayWin';

function getColor(theme: Theme, variant: ModelVariant, outcome: Outcome): string {
  if (outcome === 'draw') {
    return theme.palette.grey[500];
  }

  if (variant === 'ml') {
    return outcome === 'homeWin' ? theme.palette.primary.main : theme.palette.success.main;
  }

  return outcome === 'homeWin' ? theme.palette.warning.main : theme.palette.info.main;
}

export const sx: Record<string, SxProps<Theme>> = {
  root: {
    mb: 1.5,
  },
  rootCompact: {
    mb: 1,
  },
  labelRow: {
    mb: 0.4,
  },
  label: {
    fontWeight: 500,
    color: (theme: Theme) => theme.palette.text.secondary,
    fontSize: '0.875rem',
    maxWidth: '60%',
  },
  labelCompact: {
    fontWeight: 500,
    color: (theme: Theme) => theme.palette.text.secondary,
    fontSize: '0.78rem',
    maxWidth: '60%',
  },
  track: {
    width: '100%',
    height: 10,
    borderRadius: 5,
    bgcolor: (theme: Theme) => theme.palette.action.hover,
    overflow: 'hidden',
  },
  trackCompact: {
    width: '100%',
    height: 8,
    borderRadius: 5,
    bgcolor: (theme: Theme) => theme.palette.action.hover,
    overflow: 'hidden',
  },
};

export function getValueSx(compact: boolean, variant: ModelVariant, outcome: Outcome): SxProps<Theme> {
  return (theme: Theme) => ({
    fontWeight: 700,
    fontFeatureSettings: "'tnum'",
    fontSize: compact ? '0.78rem' : '0.875rem',
    color: getColor(theme, variant, outcome),
  });
}

export function getBarSx(widthPct: number, variant: ModelVariant, outcome: Outcome, animated: boolean): SxProps<Theme> {
  return (theme: Theme) => ({
    height: '100%',
    borderRadius: 5,
    width: `${widthPct}%`,
    bgcolor: getColor(theme, variant, outcome),
    transition: animated ? 'none' : 'width 0.6s ease',
  });
}
