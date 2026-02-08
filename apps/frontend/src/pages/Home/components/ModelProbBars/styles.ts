import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  root: {
    flex: 1,
    minWidth: 0,
  },
  title: {
    mb: 0.3,
  },
  titleCompact: {
    mb: 0.3,
    fontSize: '0.72rem',
  },
  subtitle: {
    color: (theme: Theme) => theme.palette.text.secondary,
    display: 'block',
    mb: 1,
    fontFeatureSettings: "'tnum'",
    fontSize: '0.7rem',
  },
  spacer: {
    mb: 1.2,
  },
  spacerCompact: {
    mb: 0.8,
  },
};
