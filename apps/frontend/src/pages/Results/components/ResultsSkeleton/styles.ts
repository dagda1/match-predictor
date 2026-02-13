import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  container: {
    py: { xs: 1, sm: 2 },
  },
  header: {
    px: { xs: 2, sm: 4 },
    py: { xs: 2, sm: 3 },
  },
  summary: {
    px: { xs: 2, sm: 4 },
    py: { xs: 1.5, sm: 2 },
  },
  matchCard: {
    px: { xs: 2, sm: 4 },
    py: { xs: 2, sm: 3 },
  },
};
