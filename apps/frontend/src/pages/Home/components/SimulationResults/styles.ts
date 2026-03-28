import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  card: {
    px: { xs: 2.5, sm: 4 },
    py: { xs: 2.5, sm: 4 },
  },
  progressContainer: {
    mb: 2,
  },
  progressBar: (theme: Theme) => ({
    height: 6,
    borderRadius: 3,
    bgcolor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : theme.palette.grey[200],
    '& .MuiLinearProgress-bar': {
      borderRadius: 3,
      background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.success.main} 100%)`,
    },
  }),
  predictionHeader: {
    textAlign: 'center',
    mb: { xs: 2, sm: 3 },
  },
  predictionLabel: (theme: Theme) => ({
    color: theme.palette.text.secondary,
    fontWeight: 500,
    mb: 0.3,
    fontSize: '0.75rem',
  }),
  predictionTeams: {
    fontSize: { xs: '1.05rem', sm: '1.35rem' },
    lineHeight: 1.3,
  },
  vsText: (theme: Theme) => ({
    color: theme.palette.text.disabled,
    fontWeight: 400,
    mx: 0.5,
  }),
  divider: (theme: Theme) => ({
    borderColor: theme.palette.divider,
    my: 2,
  }),
  dividerVertical: (theme: Theme) => ({
    borderColor: theme.palette.divider,
    mx: 2.5,
  }),
};
