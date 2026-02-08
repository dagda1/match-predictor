import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  container: {
    py: { xs: 1, sm: 2 },
  },
  weekPicker: {
    px: { xs: 2, sm: 4 },
    py: { xs: 2, sm: 3 },
  },
  weekTitle: {
    fontSize: { xs: '1.1rem', sm: '1.35rem' },
  },
  weekDates: {
    fontSize: '0.8rem',
    mt: 0.3,
    color: (theme: Theme) => theme.palette.text.secondary,
  },
  navButton: {
    color: (theme: Theme) => theme.palette.text.secondary,
  },
  summaryCard: {
    px: { xs: 2, sm: 4 },
    py: { xs: 1.5, sm: 2 },
  },
  summaryValue: (theme: Theme) => ({
    fontWeight: 700,
    fontSize: '1.1rem',
    fontFeatureSettings: "'tnum'",
    color: theme.palette.mode === 'dark' ? '#b09aff' : '#3D195B',
  }),
  summaryValuePoisson: (theme: Theme) => ({
    fontWeight: 700,
    fontSize: '1.1rem',
    fontFeatureSettings: "'tnum'",
    color: theme.palette.mode === 'dark' ? '#ffab40' : '#E65100',
  }),
  summaryLabel: {
    fontSize: '0.72rem',
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
    color: (theme: Theme) => theme.palette.text.secondary,
  },
  summaryDivider: {
    borderColor: (theme: Theme) =>
      theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.08)',
  },
  emptyState: {
    px: { xs: 2, sm: 4 },
    py: { xs: 4, sm: 6 },
    textAlign: 'center',
  },
  emptyText: {
    color: (theme: Theme) => theme.palette.text.secondary,
  },
};
