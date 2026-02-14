import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  dayHeader: {
    fontSize: '0.82rem',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.03em',
    color: (theme: Theme) => theme.palette.text.secondary,
    px: 0.5,
  },
};
