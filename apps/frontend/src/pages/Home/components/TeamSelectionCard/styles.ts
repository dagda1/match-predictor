import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  card: {
    px: { xs: 2.5, sm: 4 },
    py: { xs: 2.5, sm: 4 },
  },
  title: {
    mb: 0.3,
    fontSize: { xs: '1.25rem', sm: '1.5rem' },
  },
  subtitle: {
    mb: { xs: 2, sm: 3 },
  },
  teamStack: {
    mb: { xs: 2, sm: 3 },
  },
  predictButton: (theme: Theme) => ({
    py: { xs: 1.2, sm: 1.4 },
    fontSize: { xs: '0.9rem', sm: '1rem' },
    background:
      theme.palette.mode === 'dark'
        ? `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 100%)`
        : `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 100%)`,
    '&:hover': {
      background:
        theme.palette.mode === 'dark'
          ? `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.light} 100%)`
          : `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.light} 100%)`,
    },
  }),
  actionButton: {
    py: { xs: 1, sm: 1.2 },
  },
};
