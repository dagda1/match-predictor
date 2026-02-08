import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  root: {
    mb: 1.5,
  },
  rootCompact: {
    mb: 1,
  },
  labelRow: {
    mb: 0.4,
  },
  label: {
    fontWeight: 500,
    color: (theme: Theme) => theme.palette.text.secondary,
    fontSize: '0.875rem',
    maxWidth: '60%',
  },
  labelCompact: {
    fontWeight: 500,
    color: (theme: Theme) => theme.palette.text.secondary,
    fontSize: '0.78rem',
    maxWidth: '60%',
  },
  track: {
    width: '100%',
    height: 10,
    borderRadius: 5,
    bgcolor: (theme: Theme) =>
      theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : theme.palette.grey[200],
    overflow: 'hidden',
  },
  trackCompact: {
    width: '100%',
    height: 8,
    borderRadius: 5,
    bgcolor: (theme: Theme) =>
      theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.06)' : theme.palette.grey[200],
    overflow: 'hidden',
  },
};

export function valueSx(compact: boolean, color: string): SxProps<Theme> {
  return {
    fontWeight: 700,
    fontFeatureSettings: "'tnum'",
    fontSize: compact ? '0.78rem' : '0.875rem',
    color,
  };
}

export function barSx(widthPct: number, color: string, animated: boolean): SxProps<Theme> {
  return {
    height: '100%',
    borderRadius: 5,
    width: `${widthPct}%`,
    bgcolor: color,
    transition: animated ? 'none' : 'width 0.6s ease',
  };
}
