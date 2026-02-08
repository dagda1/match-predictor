import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  card: {
    px: { xs: 2, sm: 3 },
    py: { xs: 2, sm: 2.5 },
  },
  header: {
    mb: 1,
  },
  teams: {
    fontSize: { xs: '1rem', sm: '1.15rem' },
    fontWeight: 700,
    lineHeight: 1.3,
  },
  date: {
    fontSize: '0.75rem',
    color: (theme: Theme) => theme.palette.text.secondary,
  },
  predictedScores: {
    mb: { xs: 1.5, sm: 2 },
  },
  predictedLabel: {
    fontSize: '0.68rem',
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
    color: (theme: Theme) => theme.palette.text.secondary,
  },
  predictedValue: {
    fontWeight: 700,
    fontFeatureSettings: "'tnum'",
    fontSize: '0.88rem',
  },
  predictedProb: {
    fontWeight: 500,
    fontSize: '0.78rem',
    color: (theme: Theme) => theme.palette.text.secondary,
  },
};

export function mlColorSx(theme: Theme): Record<string, unknown> {
  return { color: theme.palette.mode === 'dark' ? '#b09aff' : '#3D195B' };
}

export function poissonColorSx(theme: Theme): Record<string, unknown> {
  return { color: theme.palette.mode === 'dark' ? '#ffab40' : '#E65100' };
}
