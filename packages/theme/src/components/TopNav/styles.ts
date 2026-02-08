import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  title: {
    mr: 2,
  },
  navLinks: {
    flexGrow: 1,
  },
};

export function navLinkSx(theme: Theme): Record<string, unknown> {
  const isDark = theme.palette.mode === 'dark';
  return {
    color: theme.palette.text.secondary,
    fontWeight: 500,
    fontSize: { xs: '0.82rem', sm: '0.88rem' },
    minWidth: 0,
    px: 1.5,
    borderRadius: 2,
    textDecoration: 'none',
    '&:hover': {
      bgcolor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)',
    },
    '&.active': {
      color: theme.palette.text.primary,
      fontWeight: 700,
      bgcolor: isDark ? 'rgba(124,77,255,0.12)' : 'rgba(61,25,91,0.08)',
    },
  };
}
