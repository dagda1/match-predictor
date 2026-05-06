import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  chips: {
    flexShrink: 0,
    ml: 1.5,
  },
};

export function chipSx(correct: boolean): SxProps<Theme> {
  return (theme: Theme) => ({
    fontWeight: 700,
    fontSize: '0.72rem',
    height: 24,
    border: 'none',
    bgcolor: correct
      ? `${theme.palette.success.main}1F`
      : `${theme.palette.error.main}1A`,
    color: correct
      ? theme.palette.success.main
      : theme.palette.error.main,
  });
}
