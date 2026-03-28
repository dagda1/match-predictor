import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  scoreCard: {
    px: { xs: 2.5, sm: 4 },
    py: { xs: 2.5, sm: 4 },
    flex: 1,
    minWidth: 0,
  },
  scoreSubtitle: {
    mb: 1.5,
    fontSize: { xs: '0.72rem', sm: '0.78rem' },
  },
};
