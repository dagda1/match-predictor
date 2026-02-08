import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  counter: {
    textAlign: 'center',
    color: (theme: Theme) => theme.palette.text.secondary,
    fontFeatureSettings: "'tnum'",
    mt: 0.5,
    mb: 1.5,
    fontSize: '0.8rem',
  },
};
